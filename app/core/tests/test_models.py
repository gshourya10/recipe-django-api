from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Tag


def sample_user(email='test@gmail.com', password='test123'):
    """
    Creates a sample user
    :param email: default
    :param password: default
    :return: User object
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """
        Test creating a user with email is successful
        :return: None
        """
        email = 'test@gmail.com'
        password = 'TestPass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_is_normalized(self):
        """
        Test for checking the email is normalized
        :return: None
        """
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_user_email_is_invalid(self):
        """
        Test for user email is invalid
        :return: None
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """
        Test creating new superuser
        :return: None
        """
        user = get_user_model().objects.create_superuser(
            'test@email.com',
            'test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """
        Test the string representation of tag model
        :return: None
        """
        tag = Tag.objects.create(
            user=sample_user(),
            name='Italian'
        )

        self.assertEqual(str(tag), tag.name)
