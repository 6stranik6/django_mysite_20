from typing import Sequence


from django.core.management import BaseCommand


from shopapp.models import Product


class Command(BaseCommand):

    """
    Creates order
    """

    def handle(self, *args, **options):
        self.stdout.write("Start demo select fields")
        product_values = Product.objects.values("pk", "name")
        for product in product_values:
            print(product)
        self.stdout.write(f"Done")
