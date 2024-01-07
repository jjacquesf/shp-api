"""
Tests for supplier APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from supplier.serializers import (
    SupplierSerializer
)

MAIN_URL = reverse('supplier:supplier-list')

def detail_url(id):
    return reverse('supplier:supplier-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)


def create_supplier(**params):
    return models.Supplier.objects.create(**params)

class PublicSupplierTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_suppliers_unauthorized(self):
        """Test list suppliers unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_supplier_detail_unauthorized(self):
        """Test supplier detail unauthorized"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_supplier_unauthorized(self):
        """Test creating a recipe unauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_supplier_update_unauthorized(self):
        """Test supplier update unauthorized"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_supplier_partial_update_unauthorized(self):
        """Test supplier partial update unauthorized"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenSupplierTests(TestCase):
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

    def test_list_suppliers_forbidden(self):
        """Test list suppliers forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_supplier_detail_forbidden(self):
        """Test supplier detail forbidden"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_supplier_forbidden(self):
        """Test creating a recipe forbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_supplier_update_forbidden(self):
        """Test supplier update forbidden"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_supplier_partial_update_forbidden(self):
        """Test supplier partial update forbidden"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_supplier_delete_success(self):
        """Test supplier delete success"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class SupplierTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_supplier')
        aperm = Permission.objects.get(codename='add_supplier')
        cperm = Permission.objects.get(codename='change_supplier')
        dperm = Permission.objects.get(codename='delete_supplier')

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

    def test_list_active_suppliers_success(self):
        """Test list suppliers success"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        create_supplier(**data)
        data.update({'is_active': False, 'name': 'name2', 'tax_id': 'JAFJ8611086D5', 'tax_name': 'name sa'})
        create_supplier(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        
        
        rows = models.Supplier.objects.filter(is_active=True).order_by('name')
        serializer = SupplierSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_suppliers_success(self):
        """Test list filtered suppliers success"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        create_supplier(**data)
        data.update({'is_active': False, 'name': 'name2', 'tax_id': 'JAFJ8611086D5', 'tax_name': 'name sa'})
        create_supplier(**data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Supplier.objects.all().order_by('name')
        serializer = SupplierSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)


    def test_supplier_detail_success(self):
        """Test supplier detail success"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Supplier.objects.get(id=model.id)
        serializer = SupplierSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_supplier_success(self):
        """Test creating a recipe success"""
        payload = {
            'is_active': True,
            'name': 'name3',
            'tax_id': 'JAFJ8611086D4', 
            'tax_name': 'name sa de cv'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        supplier = models.Supplier.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(supplier, k), v)

    def test_fail_creation_on_duplicated_name(self):
        """Test fail creation on duplicated name"""
        payload = {
            'is_active': True,
            'name': 'name3',
            'tax_id': 'JAFJ8611086D4', 
            'tax_name': 'name sa de cv'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_supplier_update_success(self):
        """Test supplier update success"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Supplier.objects.get(id=model.id)
        serializer = SupplierSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_supplier_partial_update_success(self):
        """Test supplier partial update success"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Supplier.objects.get(id=model.id)
        serializer = SupplierSerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_supplier_delete_success(self):
        """Test supplier delete success"""
        data = {'name': 'name1', 'tax_id': 'JAFJ8611086D4', 'tax_name': 'name sa de cv'}
        model = create_supplier(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)