from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Tests for user API (public)
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successful(self):
        """
        Test creating user with valid payload is successful
        :return: None
        """
        payload = {
            'email': 'test@email.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """
        Test creating user that already exists fails
        :return: None
        """
        payload = {
            'email': 'test@email.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test creating a user with too short password fails
        :return: None
        """
        payload = {
            'email': 'test@test.com',
            'password': 'ab',
            'name': 'Test password'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def create_token_for_user(self):
        """
        Test that a token is created for the user
        :return: None
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def create_token_invalid_credentials(self):
        """
        Test that token is not created if credentials are invalid
        :return: None
        """
        create_user(email='test@gmail.com', password='init_pass')
        payload = {'email': 'test@gmail.com', 'password': 'testpass123'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def create_token_without_user(self):
        """
        Test that token is not created if user does not exist
        :return: None
        """
        payload = {'email': 'test@gmail.com', 'password': 'testpass123'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Test that email and password are required for token generation
        :return: None
        """
        res = self.client.post(TOKEN_URL, {'email': 'random', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
