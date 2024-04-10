"""
В это модуле лежат различные наборы представлений.

Разный view для интернет-магазина: по товарам, заказам и т.д.
"""
from csv import DictWriter
from timeit import default_timer
import logging

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group, User
from django.contrib.gis.feeds import Feed
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.context_processors import PermWrapper
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.request import Request
from rest_framework.response import Response

from .common import save_csv_produts
from shopapp.forms import ProductForm, OrderForm, GroupForm
from shopapp.models import Product, Order, ProductImages
from .serializers import ProductSerializer, OrderSerializer

logger = logging.getLogger(__name__)


@extend_schema(description="Product views CRUD")
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        'name',
        'descriptions'
    ]
    filterset_fields = [
        'name',
        'descriptions',
        'price',
        'discount',
        'archived',
    ]
    ordering_fields = [
        'name',
        'descriptions',
        'price',
    ]

    @action(detail=False, methods=['get'])
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = 'products-export.csv'
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'descriptions',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(detail=False, methods=['get'], parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_produts(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves product, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found")
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class LatestProductsFeed(Feed):
    title = "Shop product (latest)"
    description = "Updates on changes in shop products."
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return (
            Product.objects
            .filter(created_at__isnull=False)
            .order_by('-created_at')[:5]
        )

    def item_title(self, item: Product) -> str:
        return item.name

    def item_description(self, item: Product) -> str:
        return item.descriptions[:100]



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        'delivery_address',
        'user_id'
    ]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "user_id",
    ]
    ordering_fields = [
        "pk",
        "delivery_address",
        "user_id",
    ]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ("laptop", 1999),
            ("desktop", 2999),
            ("smartphone", 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products
        }
        logger.debug("Products for shop index: %s", products)
        logger.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductsDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    #model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    #model = Product
    queryset = Product.objects.filter(archived=False)
    context_object_name = 'products'


class ProductsCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user

        return super().form_valid(form)

    form_class = ProductForm


class ProductsUpdateView(UserPassesTestMixin, UpdateView):

    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def test_func(self):
        return (self.request.user.is_superuser or
                (
                 self.get_object().created_by == self.request.user and
                 self.request.user.has_perm('shopapp.change_product')
                ))

    def get_success_url(self):
        return reverse('shopapp:products_details', kwargs={'pk': self.object.pk}
                       )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImages.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductsDeleteView(DeleteView):
    model = Product

    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('shopapp:order_list')


class OrderUpdateView(UpdateView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
    form_class = OrderForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse('shopapp:orders_detail', kwargs={'pk': self.object.pk}
                       )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:order_list')


def create_order(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            #Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:orders-list")
            return redirect(url)
    else:
        form = OrderForm()
    context = {
        "form": form,
    }

    return render(request, 'shopapp/create-order.html', context=context)


class ProductDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()

        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,

            }
            for product in products
        ]
        elem = products_data[0]
        name = elem["name"]
        print("name", name)
        return JsonResponse({"products": products_data})


class OrderDataExportView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:

        orders = Order.objects.order_by('pk').all()

        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user_id,
                "products": str(order.products.values_list("name"))

            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/user_orders.html"

    def get_queryset(self, **kwargs):
        owner = get_object_or_404(User, pk=self.kwargs.get("pk"))
        orders = Order.objects.filter(user=owner).all()
        context = {
            "user": owner,
            "orders": orders
        }
        print(context)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserOrderDataExportView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, **kwargs) -> JsonResponse:
        owner = get_object_or_404(User, pk=self.kwargs.get("pk"))
        cache_key = f"user_order-data-export-{owner}"
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = Order.objects.filter(user=owner).all()
            orders_data = [
                {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "promocode": order.promocode,
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)
        return JsonResponse({str(owner): orders_data})
