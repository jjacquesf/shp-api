from django.test import TestCase
from django.urls import reverse
from django.db.models import Q


from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from django.contrib.contenttypes.models import ContentType

from core import models

from permission.serializers import (
    PermissionSerializer,
)

from permission.views import (
    PermissionQuerySet
)

LIST_URL = reverse('permission:list')

def create_user(**params):
    """Create an return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicPermissionApiTest(TestCase):
    """Test the public features of the permission API"""

    def setUp(self):
        self.client = APIClient()

    def test_list_permissions_unauthorized(self):
        """Test get all permissions unauthorized."""
        res = self.client.get(LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateForbiddenPermissionApiTests(TestCase):
    """Test API requets that require authentication and user is not authorized"""

    def setUp(self):
        user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )

        self.user = user

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_permissions_forbidden(self):
        """Test get all permissions forbidden."""

        res = self.client.get(LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class PrivatePermissionApiTests(TestCase):
    """Test API requets that require authentication and user is authorized"""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_permission')
        # aperm = Permission.objects.get(codename='add_permission')
        # cperm = Permission.objects.get(codename='change_permission')
        # dperm = Permission.objects.get(codename='delete_permission')

        group.permissions.add(vperm)
        # group.permissions.add(aperm)
        # group.permissions.add(cperm)
        # group.permissions.add(dperm)

        user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )

        # print("======Assign a permission to a user========")
        # user.permissions.add(permission.pk)
        # print("======Add user to a permission========")
        group.user_set.add(user)

        # print("===user group permissions===")
        # print(user.get_group_permissions())
        # print("==============")

        self.user = user

        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_list_permissions_success(self):
        """Test get all permissions success."""
        res = self.client.get(LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        permissions = perms = PermissionQuerySet().business_domain()
        serializer = PermissionSerializer(permissions, many=True)

        self.assertEqual(res.data, serializer.data)
