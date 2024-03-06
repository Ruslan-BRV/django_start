from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse


class CardsAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_app_loads(self):
        response = self.client.get("/cards/catalog/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Каталог карточек")

    def test_card_route(self):
        response = self.client.get("/cards/catalog/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Карточка 1")

    def test_category_route(self):
        response = self.client.get("/cards/catalog/some-category-slug/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Категория some-category-slug")
