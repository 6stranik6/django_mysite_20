from django.contrib import admin

from rest_framework.routers import DefaultRouter

from django.urls import path, include
from .views import (ShopIndexView, GroupsListView,
                    ProductsDetailsView, ProductsListView,
                    ProductsUpdateView, ProductsDeleteView,
                    ProductsCreateView, ProductDataExportView,
                    OrdersListView, OrdersDetailView,
                    OrderCreateView, OrderUpdateView,
                    OrderDeleteView, OrderDataExportView,
                    ProductViewSet, OrderViewSet,
                    LatestProductsFeed, UserOrdersListView,
                    UserOrderDataExportView
                    )

app_name = "shopapp"

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(router.urls)),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export/", ProductDataExportView.as_view(), name="products_export"),
    path("products/create/", ProductsCreateView.as_view(), name="product_create"),
    path("products/<int:pk>", ProductsDetailsView.as_view(), name="products_details"),
    path("products/<int:pk>/update", ProductsUpdateView.as_view(), name="products_update"),
    path("products/<int:pk>/archive", ProductsDeleteView.as_view(), name="products_delete"),
    path("products/latest/feed/", LatestProductsFeed(), name="latest_products_feed"),

    path("orders", OrdersListView.as_view(), name="order_list"),
    path("orders/export/", OrderDataExportView.as_view(), name="orders_export"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>", OrdersDetailView.as_view(), name="orders_detail"),
    path("orders/<int:pk>/update", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/archive", OrderDeleteView.as_view(), name="order_delete"),

    path("users/<int:pk>/orders/", UserOrdersListView.as_view(), name="user_orders_list"),
    path("users/<int:pk>/orders/export/", UserOrderDataExportView.as_view(), name="user_order_explorer")

]
