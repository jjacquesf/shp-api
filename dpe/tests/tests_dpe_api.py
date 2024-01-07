"""
Tests for dpe APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from dpe.serializers import (
    DpeSerializer
)

MAIN_URL = reverse('dpe:dpe-list')

def detail_url(id):
    return reverse('dpe:dpe-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)


def create_dpe(**params):
    return models.Dpe.objects.create(**params)

class PublicDpeTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_dpes_unauthorized(self):
        """Test list dpes unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dpe_detail_unauthorized(self):
        """Test dpe detail unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_dpe_unauthorized(self):
        """Test creating a recipe unauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dpe_update_unauthorized(self):
        """Test dpe update unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dpe_partial_update_unauthorized(self):
        """Test dpe partial update unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenDpeTests(TestCase):
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

        self.client.force_authenticate(user=self.user)

    def test_list_dpes_forbidden(self):
        """Test list dpes forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_dpe_detail_forbidden(self):
        """Test dpe detail forbidden"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_dpe_forbidden(self):
        """Test creating a recipe forbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_dpe_update_forbidden(self):
        """Test dpe update forbidden"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_dpe_partial_update_forbidden(self):
        """Test dpe partial update forbidden"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_dpe_delete_success(self):
        """Test dpe delete success"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class DpeTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_dpe')
        aperm = Permission.objects.get(codename='add_dpe')
        cperm = Permission.objects.get(codename='change_dpe')
        dperm = Permission.objects.get(codename='delete_dpe')

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

        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_list_active_dpes_success(self):
        """Test list dpes success"""
        mun_data = {'name': 'name1'}
        create_dpe(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        create_dpe(**mun_data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        
        
        rows = models.Dpe.objects.filter(is_active=True).order_by('name')
        serializer = DpeSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_dpes_success(self):
        """Test list filtered dpes success"""
        mun_data = {'name': 'name1'}
        create_dpe(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        create_dpe(**mun_data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Dpe.objects.all().order_by('name')
        serializer = DpeSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)


    def test_dpe_detail_success(self):
        """Test dpe detail success"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Dpe.objects.get(id=model.id)
        serializer = DpeSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_dpe_success(self):
        """Test creating a recipe success"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        dpe = models.Dpe.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(dpe, k), v)

    def test_fail_creation_on_duplicated_name(self):
        """Test fail creation on duplicated name"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dpe_update_success(self):
        """Test dpe update success"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Dpe.objects.get(id=model.id)
        serializer = DpeSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_dpe_partial_update_success(self):
        """Test dpe partial update success"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Dpe.objects.get(id=model.id)
        serializer = DpeSerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_dpe_delete_success(self):
        """Test dpe delete success"""
        mun_data = {'name': 'name1'}
        model = create_dpe(**mun_data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)