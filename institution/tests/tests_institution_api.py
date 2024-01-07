"""
Tests for institution APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from institution.serializers import (
    InstitutionSerializer
)

MAIN_URL = reverse('institution:institution-list')

def detail_url(id):
    return reverse('institution:institution-detail', args=[id])

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


def create_institution(**params):
    return models.Institution.objects.create(**params)

class PublicInstitutionTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_institutions_unauthorized(self):
        """Test list institutions unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_institution_detail_unauthorized(self):
        """Test institution detail unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_institution_unauthorized(self):
        """Test creating a recipe unauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_institution_update_unauthorized(self):
        """Test institution update unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_institution_partial_update_unauthorized(self):
        """Test institution partial update unauthorized"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenInstitutionTests(TestCase):
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

    def test_list_institutions_forbidden(self):
        """Test list institutions forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_institution_detail_forbidden(self):
        """Test institution detail forbidden"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_institution_forbidden(self):
        """Test creating a recipe forbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_institution_update_forbidden(self):
        """Test institution update forbidden"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_institution_partial_update_forbidden(self):
        """Test institution partial update forbidden"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_institution_delete_success(self):
        """Test institution delete success"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class InstitutionTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_institution')
        aperm = Permission.objects.get(codename='add_institution')
        cperm = Permission.objects.get(codename='change_institution')
        dperm = Permission.objects.get(codename='delete_institution')

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

    def test_list_active_institutions_success(self):
        """Test list institutions success"""
        mun_data = {'name': 'name1'}
        create_institution(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        create_institution(**mun_data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        
        
        rows = models.Institution.objects.filter(is_active=True).order_by('name')
        serializer = InstitutionSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_institutions_success(self):
        """Test list filtered institutions success"""
        mun_data = {'name': 'name1'}
        create_institution(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        create_institution(**mun_data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Institution.objects.all().order_by('name')
        serializer = InstitutionSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)


    def test_institution_detail_success(self):
        """Test institution detail success"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Institution.objects.get(id=model.id)
        serializer = InstitutionSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_institution_success(self):
        """Test creating a recipe success"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        institution = models.Institution.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(institution, k), v)

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

    def test_institution_update_success(self):
        """Test institution update success"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)
        mun_data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Institution.objects.get(id=model.id)
        serializer = InstitutionSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_institution_partial_update_success(self):
        """Test institution partial update success"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)
        mun_data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), mun_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Institution.objects.get(id=model.id)
        serializer = InstitutionSerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_institution_delete_success(self):
        """Test institution delete success"""
        mun_data = {'name': 'name1'}
        model = create_institution(**mun_data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)