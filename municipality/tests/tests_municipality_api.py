"""
Tests for municipality APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from municipality.serializers import (
    MunicipalitySerializer
)

MUNICIPALITIES_URL = reverse('municipality:municipality-list')

def detail_url(id):
    return reverse('municipality:municipality-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)
    # profile_data = {
    #     "user": user,
    #     "job_position": "CTO"
    # }
    # models.Profile.objects.create(**profile_data)
    return user

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)


def create_municipality(**params):
    return models.Municipality.objects.create(**params)

class PublicMunicipalityTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_municipalities_unauthorized(self):
        """Test list municipalities unauthorized"""
        res = self.client.get(MUNICIPALITIES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_municipality_detail_unauthorized(self):
        """Test municipality detail unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_municipality_unauthorized(self):
        """Test creating a recipe unauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MUNICIPALITIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_municipality_update_unauthorized(self):
        """Test municipality update unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_municipality_partial_update_unauthorized(self):
        """Test municipality partial update unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenMunicipalityTests(TestCase):
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

    def test_list_municipalities_forbidden(self):
        """Test list municipalities forbidden"""
        res = self.client.get(MUNICIPALITIES_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_municipality_detail_forbidden(self):
        """Test municipality detail forbidden"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_municipality_forbidden(self):
        """Test creating a recipe forbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MUNICIPALITIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_municipality_update_forbidden(self):
        """Test municipality update forbidden"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_municipality_partial_update_forbidden(self):
        """Test municipality partial update forbidden"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_municipality_delete_success(self):
        """Test municipality delete success"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class MunicipalityTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_municipality')
        aperm = Permission.objects.get(codename='add_municipality')
        cperm = Permission.objects.get(codename='change_municipality')
        dperm = Permission.objects.get(codename='delete_municipality')

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

    def test_list_municipalities_success(self):
        """Test list municipalities success"""
        mun_data = {'name': 'name1'}
        create_municipality(**mun_data)
        mun_data.update({'name': 'name2'})
        create_municipality(**mun_data)

        res = self.client.get(MUNICIPALITIES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Municipality.objects.all().order_by('name')
        serializer = MunicipalitySerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)


    def test_municipality_detail_success(self):
        """Test municipality detail success"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Municipality.objects.get(id=model.id)
        serializer = MunicipalitySerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_municipality_success(self):
        """Test creating a recipe success"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MUNICIPALITIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        municipality = models.Municipality.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(municipality, k), v)

    def test_fail_creation_on_duplicated_name(self):
        """Test fail creation on duplicated name"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MUNICIPALITIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.post(MUNICIPALITIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_municipality_update_success(self):
        """Test municipality update success"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Municipality.objects.get(id=model.id)
        serializer = MunicipalitySerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_municipality_partial_update_success(self):
        """Test municipality partial update success"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Municipality.objects.get(id=model.id)
        serializer = MunicipalitySerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_municipality_delete_success(self):
        """Test municipality delete success"""
        mun_data = {'name': 'name1'}
        model = create_municipality(**mun_data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
