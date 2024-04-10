from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User
from django.db import models


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename
    )



class Product(models.Model):
    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("Product")
    name = models.CharField(max_length=100, db_index=True)
    descriptions = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, default=1)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    #@property
    #def description_short(self) -> str:
    #    if len(self.descriptions) < 48:
    #        return self.descriptions
    #    return self.descriptions[:48] + "..."
    def __str__(self) -> str:
        return f"Product(pk={self.pk}, name={self.name!r})"

    def get_absolute_url(self):
        return reverse('shopapp:products_details', kwargs={'pk': self.pk})


def products_images_directory_path(instance: "ProductImages", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename
    )


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products_images_directory_path', blank=True, null=True)
    description = models.CharField(null=False, blank=True, max_length=200)


class Order(models.Model):
    class Meta:
        verbose_name = _("Order")
    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(upload_to="orders/receipts", null=True)
