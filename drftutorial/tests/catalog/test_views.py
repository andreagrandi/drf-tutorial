import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestProductList(APITestCase):
    @pytest.mark.django_db
    def test_can_get_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 8)
