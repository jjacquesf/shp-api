from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core import models

from group.serializers import (
    GroupSerializer,
    PermissionSerializer,
)

LIST_CREATE_URL = reverse('group:list_create')

def get_manage_url(id):
    return reverse('group:manage', args=[id])


def get_group_permissions_url(id):
    return reverse('group:permission', args=[id])

def create_user(**params):
    """Create an return a new user"""
    return get_user_model().objects.create_user(**params)

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)

class PublicGroupApiTest(TestCase):
    """Test the public features of the group API"""

    def setUp(self):
        self.client = APIClient()

    def test_list_groups_unauthorized(self):
        """Test get all groups unauthorized."""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        create_group(**details)

        # res = self.client.get(LIST_URL)
        res = self.client.get(LIST_CREATE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_unauthorized(self):
        """Test creating a group unauthorized"""
        payload = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        # res = self.client.post(CREATE_URL, payload)
        res = self.client.post(LIST_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_unauthorized(self):
        """Test creating a group unauthorized"""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)

        payload = {
            'name': 'newtest'
        }
        res = self.client.patch(get_manage_url(group.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_unauthorized(self):
        """Test delete a group unauthorized"""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)

        payload = {
            'name': 'newtest'
        }
        res = self.client.delete(get_manage_url(group.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_group_permissions_unauthorized(self):
        """Test list group permissions unauthorized"""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)
        res = self.client.get(get_group_permissions_url(group.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_permissions_to_group_unauthorized(self):
        """Test update permissions to a group unauthorized"""
        details = {
            'name': 'testgroup2',
            'description': 'Test group',
        }
        group = create_group(**details)

        payload = {
            "permissions": [
                "view_user",
                "delete_customgroup",
            ]
        }
        res = self.client.put(get_group_permissions_url(group.id), payload, 'json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateForbiddenGroupApiTests(TestCase):
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

    def test_list_groups_forbidden(self):
        """Test get all groups forbidden."""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        create_group(**details)

        # res = self.client.get(LIST_URL)
        res = self.client.get(LIST_CREATE_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_forbidden(self):
        """Test creating a group successfull"""
        payload = {
            'name': 'testgroup2',
            'description': 'Test group2',
        }
        # res = self.client.post(CREATE_URL, payload)
        res = self.client.post(LIST_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_forbidden(self):
        """Test creating a group forbidden"""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)

        payload = {
            'name': 'newtest'
        }
        res = self.client.patch(get_manage_url(group.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_forbidden(self):
        """Test delete a group forbidden"""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)

        res = self.client.delete(get_manage_url(group.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_group_permissions_forbidden(self):
        """Test list group permissions forbidden"""

        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)

        res = self.client.get(get_group_permissions_url(group.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_permissions_to_group_forbidden(self):
        """Test update permissions to a group forbidden"""
        details = {
            'name': 'testgroup2',
            'description': 'Test group',
        }
        group = create_group(**details)

        payload = {
            "permissions": [
                "view_user",
                "delete_customgroup",
            ]
        }
        res = self.client.put(get_group_permissions_url(group.id), payload, 'json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class PrivateGroupApiTests(TestCase):
    """Test API requets that require authentication and user is authorized"""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_customgroup')
        aperm = Permission.objects.get(codename='add_customgroup')
        cperm = Permission.objects.get(codename='change_customgroup')
        dperm = Permission.objects.get(codename='delete_customgroup')

        group.permissions.add(vperm)
        group.permissions.add(aperm)
        group.permissions.add(cperm)
        group.permissions.add(dperm)

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


        # content_type = ContentType.objects.get_for_model(get_user_model())
        # content_type2 = ContentType.objects.get_for_model(models.CustomGroup)
        # user_permission = Permission.objects.filter(Q(content_type=content_type) | Q(content_type=content_type2))
        # print(user_permission)

        self.group = group

        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_list_groups_success(self):
        """Test get all groups success."""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        create_group(**details)

        # res = self.client.get(LIST_URL)
        res = self.client.get(LIST_CREATE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        groups = models.CustomGroup.objects.all().order_by('-id')
        serializer = GroupSerializer(groups, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_create_success(self):
        """Test creating a group success"""
        payload = {
            'name': 'testgroup2',
            'description': 'Test group2',
        }
        res = self.client.post(LIST_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        group = models.CustomGroup.objects.get(name=payload['name'])
        serializer = GroupSerializer(group)

        self.assertEqual(res.data, serializer.data)

    def test_change_success(self):
        """Test creating a group success"""
        payload = {
            'name': 'newtest'
        }
        res = self.client.patch(get_manage_url(self.group.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        group = models.CustomGroup.objects.get(name=payload['name'])
        serializer = GroupSerializer(group)

        self.assertEqual(res.data, serializer.data)

    def test_delete_success(self):
        """Test delete a group success"""
        details = {
            'name': 'testgroup',
            'description': 'Test group',
        }
        group = create_group(**details)

        payload = {
            'name': 'newtest'
        }
        res = self.client.delete(get_manage_url(group.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_group_permissions_success(self):
        """Test list group permissions success"""
        res = self.client.get(get_group_permissions_url(self.group.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = PermissionSerializer(self.group.permissions.all(), many=True)
        self.assertEqual(serializer.data, res.data)

    def test_update_permissions_to_group_success(self):
        """Test update permissions to a group success"""
        details = {
            'name': 'testgroup2',
            'description': 'Test group',
        }
        group = create_group(**details)

        payload = {
            "permissions": [
                "view_user",
                "delete_customgroup",
            ]
        }
        res = self.client.put(get_group_permissions_url(group.id), payload, 'json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        perms = Permission.objects.filter(Q(codename="view_user") | Q(codename="delete_customgroup"))
        serializer = PermissionSerializer(perms, many=True)

        self.assertEqual(serializer.data, res.data)