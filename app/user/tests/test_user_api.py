from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_create_token_for_user(self):
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

    def test_create_token_invalid_credentials(self):
        """
        Test that token is not created if credentials are invalid
        :return: None
        """
        create_user(email='test@gmail.com', password='init_pass')
        payload = {'email': 'test@gmail.com', 'password': 'testpass123'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_without_user(self):
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

    def test_retrieve_user_unauthorized(self):
        """
        Test that retrieves an user with authentication fails
        :return: None
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Tests that require authentication of the user
    """
    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='test_pass',
            name='test name'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_successful(self):
        """
        Test that retrieves user profile
        :return: None
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """
        Test that POST method is not allowed on me url
        :return: None
        """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test updating the user profile for authenticated user
        :return: None
        """
        payload = {
            'name': 'New name',
            'password': 'new password'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
