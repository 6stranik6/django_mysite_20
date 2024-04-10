from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_produts, save_csv_orders
from .models import Product, Order, ProductImages
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImages


@admin.action(description="Archive product")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive product")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"

    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "archived",
    list_display_links = "pk", "name"
    ordering = "name", "pk"
    search_fields = "name", "descriptions", "price", "discount"
    fieldsets = [
        (None, {
            "fields": ("name", "descriptions"),
                }),
        ("price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse",),
        }),
        ("images", {
            "fields": ("preview",),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is fir soft delete"
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.descriptions) < 48:
            return obj.descriptions
        return obj.descriptions[:48] + "..."

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {"form": form}
            return render(request, "admin/csv-form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {"form": form}
            return render(request, "admin/csv-form.html", context, status=400)

        save_csv_produts(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )
        self.message_user(request, "Data from CSV imported successfully")
        return redirect("..")

    def get_urls(self):
        urls = super(ProductAdmin, self).get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv"
            ),
        ]
        return new_urls + urls


class PruductInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/orders_changelist.html"

    inlines = [
        PruductInline,
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {"form": form}
            return render(request, "admin/csv-form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {"form": form}
            return render(request, "admin/csv-form.html", context, status=400)

        save_csv_orders(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )
        self.message_user(request, "Data from CSV imported successfully")
        return redirect("..")

    def get_urls(self):
        urls = super(OrderAdmin, self).get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv"
            ),
        ]
        return new_urls + urls
