"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from django.contrib.auth.models import Permission

from user.serializers import (
    UserSerializer,
    UserProfileSerializer
)

from group.serializers import (
    GroupSerializer,
)

LIST_USER_URL = reverse('user:list')
CREATE_USER_URL = reverse('user:create')

def get_user_detail_url(user_id):
    return reverse('user:detail', args=[user_id])

def get_user_groups_url(user_id):
    return reverse('user:group', args=[user_id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)
    profile_data = {
        "user": user,
        "job_position": "CTO"
    }
    profile = models.Profile.objects.create(**profile_data)
    return user

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)

class PublicUserManagementApiTests(TestCase):
    """Test User management public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_list_users_not_allowed(self):
        """Test get all users not allowed."""
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
        res = self.client.get(get_user_detail_url(user.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserManagementApiTests(TestCase):
    """Test User management API requets that require authentication"""

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
        """Test creating a user is successfull success"""
        payload = {
            "email": "user@user.com",
            "name": "Jhon Doe",
            "job_position": "CTO",
            "password": "123456"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    # def test_user_with_email_exists_error(self):
    #         """Test error returned if user with email exists."""
    #         payload = {
    #             'email': 'test@example.com',
    #             'password': 'testpass123',
    #             'name': 'Test Name',
    #         }
    #         res = self.client.post(CREATE_USER_URL, payload)

    #         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def retrieve_profile_success(self):
        """Test retrieving profile for logged in user success"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    # def test_password_too_sort_error(self):
    #     """Test an error is returned if password less than 5 chars"""
    #     payload = {
    #         'email': 'nonexisting@example.com',
    #         'password': 'pw',
    #         'name': 'Test name'
    #     }
    #     res = self.client.post(CREATE_USER_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    #     user_exist = get_user_model().objects.filter(
    #         email=payload['email']
    #     ).exists()
    #     self.assertFalse(user_exist)

    def test_list_user_success(self):
        """Test get all users success."""
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

    def test_retrieve_user_success(self):
        """Test retrieve user success."""
        res = self.client.get(get_user_detail_url(self.user.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user = get_user_model().objects.get(email=self.user.email)
        profile = models.Profile.objects.get(user=user)

        serializer = UserProfileSerializer({
            "name": user.name,
            "email": user.email,
            "job_position": profile.job_position
        })

        self.assertEqual(res.data, serializer.data)
        
    def test_list_user_groups_success(self):
        """Test get all user group success."""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)

        group.user_set.add(self.user)

        res = self.client.get(get_user_groups_url(self.user.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        groups = self.user.groups.all()
        serializer = GroupSerializer(groups, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_set_user_to_a_group_success(self):
        """Test set user groups success."""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)

        details = {
            'name': 'testgroup2',
            'description': 'Test group',
        }
        group2 = create_group(**details)

        payload = {
            'groups': [
                group.id,
                group2.id
            ]
        }

        res = self.client.put(get_user_groups_url(self.user.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        groups = self.user.groups.all()
        serializer = GroupSerializer(groups, many=True)

        self.assertEqual(res.data, serializer.data)