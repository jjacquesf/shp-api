"""
Tests forSIAN userAPIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from sianuser.serializers import (
    SianUserSerializer
)

MAIN_URL = reverse('sianuser:sianuser-list')

def detail_url(id):
    return reverse('sianuser:sianuser-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_stateorg(**params):
    """Create an return a new group"""
    return models.StateOrg.objects.create(**params)


def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)


def create_sianuser(**params):
    return models.SianUser.objects.create(**params)

class PublicSianUserTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

        stateorg = create_stateorg(name="State Org")
        self.stateorg = stateorg


    def test_list_sian_users_unauthorized(self):
        """Test list SIAN users unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sian_user_detail_unauthorized(self):
        """Test SIAN userdetail unauthorized"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_sian_user_unauthorized(self):
        """Test creating aSIAN userunauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sian_user_update_unauthorized(self):
        """Test SIAN userupdate unauthorized"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sian_user_partial_update_unauthorized(self):
        """Test SIAN userpartial update unauthorized"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenSianUserTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

        user_data = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }

        user = create_user(**user_data)
        self.user = user

        stateorg = create_stateorg(name="State Org")
        self.stateorg = stateorg

        self.client.force_authenticate(user=self.user)

    def test_list_sian_users_forbidden(self):
        """Test list SIAN users forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sian_user_detail_forbidden(self):
        """Test SIAN userdetail forbidden"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_sian_user_forbidden(self):
        """Test creating aSIAN userforbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sian_user_update_forbidden(self):
        """Test SIAN userupdate forbidden"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sian_user_partial_update_forbidden(self):
        """Test SIAN userpartial update forbidden"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sian_user_delete_success(self):
        """Test SIAN userdelete success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class SianUserTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_sianuser')
        aperm = Permission.objects.get(codename='add_sianuser')
        cperm = Permission.objects.get(codename='change_sianuser')
        dperm = Permission.objects.get(codename='delete_sianuser')

        group.permissions.add(vperm)
        group.permissions.add(aperm)
        group.permissions.add(cperm)
        group.permissions.add(dperm)

        user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
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

        stateorg = create_stateorg(name="State Org")
        self.stateorg = stateorg

        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_list_active_sian_users_success(self):
        """Test list SIAN users success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        create_sianuser(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_sianuser(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
                
        rows = models.SianUser.objects.filter(is_active=True).order_by('name')
        serializer = SianUserSerializer(rows, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_sian_users_success(self):
        """Test list filtered SIAN users success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        create_sianuser(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_sianuser(**data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.SianUser.objects.all().order_by('name')
        serializer = SianUserSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_sian_user_detail_success(self):
        """Test SIAN userdetail success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.SianUser.objects.get(id=model.id)
        serializer = SianUserSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_sian_user_success(self):
        """Test creating aSIAN usersuccess"""
        payload = {
            'is_active': True,
            'name': 'name3',
            'stateorg': self.stateorg.id
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        sianuser = models.SianUser.objects.get(id=res.data['id'])
        for k,v in payload.items():
            if k == 'stateorg':
                self.assertEqual(getattr(sianuser, k).id, v)
            else:
                self.assertEqual(getattr(sianuser, k), v)

    def test_fail_creation_on_duplicated_name(self):
        """Test fail creation on duplicated name"""
        payload = {
            'is_active': True,
            'name': 'name3',
            'stateorg': self.stateorg.id
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sian_user_update_success(self):
        """Test SIAN userupdate success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)
        data.update({'is_active': False, 'name': 'name2', 'stateorg': self.stateorg.id})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.SianUser.objects.get(id=model.id)
        serializer = SianUserSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_sian_user_partial_update_success(self):
        """Test SIAN userpartial update success"""
        data = {'name': 'name10', 'stateorg': self.stateorg}
        model = create_sianuser(**data)
        data = {'name': 'name10', 'stateorg': self.stateorg.id}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.SianUser.objects.get(id=model.id)
        serializer = SianUserSerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_sian_user_delete_success(self):
        """Test SIAN userdelete success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sianuser(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)