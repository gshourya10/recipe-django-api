from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from ..serializers import IngredientSerializer
from core.models import Ingredient

from rest_framework import status
from rest_framework.test import APIClient

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """
    Tests publicly available ingredient APIs
    """
    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """
        Tests that login is required
        :return: None
        """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """
    Tests ingredient APIS with authenticated user
    """
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """
        Test retrieving list of ingredients
        :return: None
        """
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Spinach')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_ingredients_limited_to_user(self):
        """
        Test the ingredients are limited to the authenticated user
        :return: None
        """
        Ingredient.objects.create(
            user=get_user_model().objects.create_user(
                email='other@gmail.com',
                password='testpass'
            ),
            name='Carrot'
        )
        ingredient = Ingredient.objects.create(user=self.user, name='Coconut')
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_creating_ingredients_successful(self):
        """
        Test creating ingredients successful
        :return: None
        """
        payload = {
            'name': 'Cucumber'
        }
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_creating_ingredients_invalid(self):
        """
        Test creating ingredients with invalid payload
        :return: None
        """
        res = self.client.post(INGREDIENTS_URL, {'name': ''})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
