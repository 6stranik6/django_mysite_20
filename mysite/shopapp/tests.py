import json

from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product, Order
from django.utils.translation import activate

activate('en')


class ProductCreateViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test", password="111")
        permission = Permission.objects.get(codename="add_product")
        cls.user.user_permissions.add(permission)


    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.product_name = 'Test Product Name'

    def tearDown(self):
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": '123,33',
                "description": 'test desc',
                "discount": '11',
            },
            HTTP_USER_AGENT='Mozilla/5.0'
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists(),
        )


class ProductsDetailsViewTestCase(TestCase):
    #@classmethod
    #def setUpClass(cls):
        #cls.user = User.objects.create_user(username='test', password='111')
        #cls.product = Product.objects.create(name='test')

    #@classmethod
    #def tearDownClass(cls):
        #cls.user.delete()
        #cls.product.delete()

    def setUp(self):
        #self.client.force_login(self.user)
        self.product = Product.objects.create(name='test')

    def tearDown(self):
        self.product.delete()
    def test_get_product_and_check_content(self):
        response = self.client.get(reverse("shopapp:products_details",
                                           kwargs={"pk": self.product.pk}), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, 200)

    def test_get_product(self):
        response = self.client.get(reverse("shopapp:products_details",
                                           kwargs={"pk": self.product.pk}), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertContains(response, self.product.name)


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='111')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:order_list'), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertContains(response, "Orders")


class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test", password="111")
        permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(
                                         delivery_address='123 fdggf',
                                         promocode="promo",
                                         user_id=self.user.id,
                                         )

    def tearDown(self):
        Order.objects.filter(pk=self.order.pk).delete()

    def test_order_details(self):
        response = self.client.get(reverse("shopapp:orders_detail", kwargs={"pk": self.order.pk}),
                                   HTTP_USER_AGENT="Mozilla/5.0"
                                   )

        self.assertContains(response, "123 fdggf")
        self.assertContains(response, "promo")
        self.assertTrue(
            Order.objects.filter(pk=self.order.pk).exists(),
        )


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'user-fixture.json',
        'products-fixture.json',
        'groups-fixture.json'


    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products_export"), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, 200)

        products = Product.objects.order_by('pk').all()
        #users = User.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,


            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data
        )


class OrderExportViewTestCase(TestCase):
    fixtures = [
        'user-fixture.json',
        'products-fixture.json',
        'groups-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = (User.objects.create_user(username='test', password='111', is_staff=True)
                    )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:orders_export"), HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(response.status_code, 200)

        orders = Order.objects.order_by('pk').all()

        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user_id,
                "products": str(order.products.values_list("name"))

            }
            for order in orders
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["orders"],
            expected_data
        )
