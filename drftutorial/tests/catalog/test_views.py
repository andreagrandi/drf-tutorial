import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from catalog.models import Product, Review


UserModel = get_user_model()


class APIAdminAPITestCase(APITestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.user = UserModel.objects.create_superuser(
            username='test', email='test@...', password='top_secret')
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class APIUserAPITestCase(APITestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username='test', email='test@...', password='top_secret')
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Create a review for a product
        url = reverse('review-list', kwargs={'product_id': 1})
        data = {
            "title": "Best food ever",
            "review": "Really the best food I have ever tried",
            "rating": 5
        }
        self.client.post(url, data, format='json')


class TestProductListAnonymous(APITestCase):
    @pytest.mark.django_db
    def test_can_get_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 8)


class TestProductListAdmin(APIAdminAPITestCase):
    @pytest.mark.django_db
    def test_admin_can_post_new_product(self):
        url = reverse('product-list')

        data = {
            "description": "Sbriciolona",
            "name": "Sbriciolona",
            "price": "8.50"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 9)

    @pytest.mark.django_db
    def test_anonymous_cannot_post_new_product(self):
        url = reverse('product-list')

        data = {
            "description": "Sbriciolona",
            "name": "Sbriciolona",
            "price": "8.50"
        }

        self.client.logout()
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.count(), 8)


class TestProductDetailAnonymous(APITestCase):
    @pytest.mark.django_db
    def test_can_get_product_detail(self):
        url = reverse('product-detail', kwargs={'product_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestProductDetailAdmin(APIAdminAPITestCase):
    @pytest.mark.django_db
    def test_admin_can_delete_a_product(self):
        url = reverse('product-detail', kwargs={'product_id': 1})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 7)

    @pytest.mark.django_db
    def test_anonymous_cannot_delete_a_product(self):
        url = reverse('product-detail', kwargs={'product_id': 1})

        # Logout so the user is anonymous
        self.client.logout()

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.count(), 8)

    @pytest.mark.django_db
    def test_admin_can_update_a_product(self):
        url = reverse('product-detail', kwargs={'product_id': 1})

        data = {
            "name": "Salame",
            "description": "Salame Toscano autentico",
            "price": "8.60"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 8)
        self.assertEqual(response.json()['price'], '8.60')
        self.assertEqual(
            response.json()['description'], 'Salame Toscano autentico')

    @pytest.mark.django_db
    def test_admin_can_patch_a_product(self):
        url = reverse('product-detail', kwargs={'product_id': 1})

        data = {
            "price": "8.60"
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 8)
        self.assertEqual(response.json()['price'], '8.60')


class TestReviewListAnonymous(APIUserAPITestCase):
    @pytest.mark.django_db
    def test_can_get_review_list(self):
        self.client.logout()
        url = reverse('review-list', kwargs={'product_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)


class TestReviewListUser(APIUserAPITestCase):
    @pytest.mark.django_db
    def test_user_can_post_review(self):
        url = reverse('review-list', kwargs={'product_id': 2})
        data = {
            "title": "The best!",
            "review": "Really the best food I have ever tried",
            "rating": 5
        }
        self.client.post(url, data, format='json')

        # Check the Review has been posted
        url = reverse('review-list', kwargs={'product_id': 2})
        response = self.client.get(url)
        self.assertEqual(
            response.json()[0]['title'], 'The best!')

    @pytest.mark.django_db
    def test_anonymous_cannot_post_review(self):
        self.client.logout()
        url = reverse('review-list', kwargs={'product_id': 2})
        data = {
            "title": "The best!",
            "review": "Really the best food I have ever tried",
            "rating": 5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestReviewDetailAnonymous(APIUserAPITestCase):
    @pytest.mark.django_db
    def test_anonymous_can_get_single_review(self):
        self.client.logout()
        url = reverse(
            'review-detail', kwargs={'product_id': 1, 'review_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], 'Best food ever')


class TestReviewDetailUser(APIUserAPITestCase):
    @pytest.mark.django_db
    def test_user_can_update_single_review(self):
        url = reverse(
            'review-detail', kwargs={'product_id': 1, 'review_id': 1})
        data = {
            "title": "Best food ever",
            "review": "Really the best food I have ever tried",
            "rating": 4
        }
        self.client.put(url, data, format='json')

        # Check the Review has been updated
        url = reverse('review-list', kwargs={'product_id': 1})
        response = self.client.get(url)
        self.assertEqual(
            response.json()[0]['rating'], 4)

    @pytest.mark.django_db
    def test_user_can_patch_single_review(self):
        url = reverse(
            'review-detail', kwargs={'product_id': 1, 'review_id': 1})
        data = {
            "rating": 4
        }
        self.client.patch(url, data, format='json')

        # Check the Review has been updated
        url = reverse('review-list', kwargs={'product_id': 1})
        response = self.client.get(url)
        self.assertEqual(
            response.json()[0]['rating'], 4)

    @pytest.mark.django_db
    def test_user_can_delete_own_review(self):
        url = reverse(
            'review-detail', kwargs={'product_id': 1, 'review_id': 1})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    @pytest.mark.django_db
    def test_user_cannot_delete_another_user_review(self):
        # Logout main User
        self.client.logout()

        # Create a new user
        self.user_2 = UserModel.objects.create_user(
            username='test_2', email='test_2@...', password='top_secret')
        token = Token.objects.create(user=self.user_2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse(
            'review-detail', kwargs={'product_id': 1, 'review_id': 1})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
