from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from ..serializers import TagSerializer
from core.models import Tag

from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """
    Tests for publicly available tags API1
    """
    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """
        Tests that login is required
        :return: None
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Tests for authorized tags API
    """
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            'test@gmail.com', 'test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test to retrieve tags
        :return: None
        """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tags_limited_to_user(self):
        """
        Test retrieving tags limited to authenticated user
        :return: None
        """
        tag = Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(
            user=get_user_model().objects.create_user(
                'test2@gmail.com',
                'test123'
            ),
            name='Bakery')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_creating_tag_successful(self):
        """
        Test creating new tags is successful
        :return: None
        """
        payload = {
            'name': 'new name'
        }
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_creating_tag_invalid(self):
        """
        Test creating a new tag with invalid payload
        :return: None
        """
        payload = {
            'name': ''
        }
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
