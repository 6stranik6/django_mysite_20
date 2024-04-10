from rest_framework import serializers

from .models import Product
from .models import Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "descriptions",
            "price",
            "discount",
            "created_at",
            "archived",
            "preview",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "pk",
            "delivery_address",
            "promocode",
            "user_id",
            "created_at",
        )
