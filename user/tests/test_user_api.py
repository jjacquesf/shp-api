"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from django.contrib.auth.models import Group, Permission

from user.serializers import (
    UserSerializer,
)

LIST_USER_URL = reverse('user:list')
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def get_retrive_url(user_id):
    return reverse('user:retrieve', args=[user_id])

def create_user(**params):
    """Create an return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTest(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        user_details = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res =  self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test return error if credentials invalid"""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpassord'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test autentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_user_not_allowed(self):
        """Test get all users."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.get(LIST_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_not_allowed(self):
        """Test retrieve user not allowed."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        user = create_user(**payload)
        res = self.client.get(get_retrive_url(user.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """Test API requets that require authentication"""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='admin')
        
        vperm = Permission.objects.get(codename='view_user')
        aperm = Permission.objects.get(codename='add_user')
        cperm = Permission.objects.get(codename='change_user')

        group.permissions.add(vperm)
        group.permissions.add(aperm)
        group.permissions.add(cperm)

        user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )

        # print("======Assign a group to a user========")
        # user.groups.add(group.pk)
        # print("======Add user to a group========")
        group.user_set.add(user)

        # print("===user group permissions===")
        # print(user.get_group_permissions())
        # print("==============")

        self.user = user

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_success(self):
        """Test creating a user is successfull"""
        payload = {
            'email': 'nonexisting@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
            """Test error returned if user with email exists."""
            payload = {
                'email': 'test@example.com',
                'password': 'testpass123',
                'name': 'Test Name',
            }
            res = self.client.post(CREATE_USER_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed fot the me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user"""
        payload = {'name': 'Updated anme', 'password': 'updatedpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_password_too_sort_error(self):
        """Test an error is returned if password less than 5 chars"""
        payload = {
            'email': 'nonexisting@example.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_list_user(self):
        """Test get all users."""
        payload = {
            'email': 'test2@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.get(LIST_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        users = get_user_model().objects.all().order_by('-id')
        serializer = UserSerializer(users, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_retrieve_user(self):
        """Test retrieve user."""
        res = self.client.get(get_retrive_url(self.user.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user = get_user_model().objects.get(email=self.user.email)

        serializer = UserSerializer(user)

        self.assertEqual(res.data, serializer.data)
        
