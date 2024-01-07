"""
Tests forSIF userAPIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from sifuser.serializers import (
    SifUserSerializer
)

MAIN_URL = reverse('sifuser:sifuser-list')

def detail_url(id):
    return reverse('sifuser:sifuser-detail', args=[id])

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


def create_sifuser(**params):
    return models.SifUser.objects.create(**params)

class PublicSifUserTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

        stateorg = create_stateorg(name="State Org")
        self.stateorg = stateorg


    def test_list_sif_users_unauthorized(self):
        """Test list SIF users unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sif_user_detail_unauthorized(self):
        """Test SIF userdetail unauthorized"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_sif_user_unauthorized(self):
        """Test creating aSIF userunauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sif_user_update_unauthorized(self):
        """Test SIF userupdate unauthorized"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sif_user_partial_update_unauthorized(self):
        """Test SIF userpartial update unauthorized"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenSifUserTests(TestCase):
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

    def test_list_sif_users_forbidden(self):
        """Test list SIF users forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sif_user_detail_forbidden(self):
        """Test SIF userdetail forbidden"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_sif_user_forbidden(self):
        """Test creating aSIF userforbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sif_user_update_forbidden(self):
        """Test SIF userupdate forbidden"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sif_user_partial_update_forbidden(self):
        """Test SIF userpartial update forbidden"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sif_user_delete_success(self):
        """Test SIF userdelete success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class SifUserTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_sifuser')
        aperm = Permission.objects.get(codename='add_sifuser')
        cperm = Permission.objects.get(codename='change_sifuser')
        dperm = Permission.objects.get(codename='delete_sifuser')

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

    def test_list_active_sif_users_success(self):
        """Test list SIF users success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        create_sifuser(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_sifuser(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
                
        rows = models.SifUser.objects.filter(is_active=True).order_by('name')
        serializer = SifUserSerializer(rows, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_sif_users_success(self):
        """Test list filtered SIF users success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        create_sifuser(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_sifuser(**data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.SifUser.objects.all().order_by('name')
        serializer = SifUserSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_sif_user_detail_success(self):
        """Test SIF userdetail success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.SifUser.objects.get(id=model.id)
        serializer = SifUserSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_sif_user_success(self):
        """Test creating aSIF usersuccess"""
        payload = {
            'is_active': True,
            'name': 'name3',
            'stateorg': self.stateorg.id
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        sifuser = models.SifUser.objects.get(id=res.data['id'])
        for k,v in payload.items():
            if k == 'stateorg':
                self.assertEqual(getattr(sifuser, k).id, v)
            else:
                self.assertEqual(getattr(sifuser, k), v)

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

    def test_sif_user_update_success(self):
        """Test SIF userupdate success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)
        data.update({'is_active': False, 'name': 'name2', 'stateorg': self.stateorg.id})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.SifUser.objects.get(id=model.id)
        serializer = SifUserSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_sif_user_partial_update_success(self):
        """Test SIF userpartial update success"""
        data = {'name': 'name10', 'stateorg': self.stateorg}
        model = create_sifuser(**data)
        data = {'name': 'name10', 'stateorg': self.stateorg.id}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.SifUser.objects.get(id=model.id)
        serializer = SifUserSerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_sif_user_delete_success(self):
        """Test SIF userdelete success"""
        data = {'name': 'name1', 'stateorg': self.stateorg}
        model = create_sifuser(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)