"""
Tests for entity APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

import eav
from eav.models import Attribute

from core import models 
from eav.models import Attribute

from custom_field.serializers import (
    CustomFieldSerializer
)

MAIN_URL = reverse('customfield:customfield-list')

def detail_url(id):
    return reverse('customfield:customfield-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)
    return user

def create_custom_field(**params):
    """Create an return a new custom field"""
    model = Attribute.objects.create(**params)
    return model

class PublicCustomFieldTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    # def test_custom_attrs(self):
    #     """Test demo"""
    #     attr = Attribute.objects.create(name='Color', slug='color', datatype=Attribute.TYPE_TEXT)
    #     attr2 = Attribute.objects.create(name='Type', slug='type', datatype=Attribute.TYPE_TEXT)

    #     attrv = 'color'
    #     data = {'name': 'name1', 'alias': 'name1', f'eav__{attrv}': 'red'}
    #     model = models.EvidenceGroup.objects.create(**data)

    #     data2 = {'name': 'name2', 'alias': 'name2', 'eav__type': 'specific'}
    #     model2 = models.EvidenceGroup.objects.create(**data2)
    #     print('====')
    #     print('====')
    #     print('====')
    #     print(model.eav_values.all())
    #     print('====')
    #     print('====')
    #     print(model2.eav_values.all())
    #     print('====')
    #     print('====')
    #     # found = Attribute.objects.filter(slug='color')
    #     # print('found')
    #     # print(found[0])
    #     # print('====')
    #     # print('====')


    def test_list_custom_fields_unauthorized(self):
        """Test list custom fields unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_custom_fields_unauthorized(self):
        """Test create custom fields unauthorized"""
        payload = {
            "description": "Custom 1 field description",
            "attribute_name": "custom 1", 
            "attribute_slug": "custom1", 
            "attribute_datatype": Attribute.TYPE_TEXT,
        }

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_custom_fields_unauthorized(self):
        """Test update custom fields unauthorized"""
        model = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom 1 field description"
        )

        res = self.client.patch(detail_url(model.id), {
            'is_active': False,
            'description': "Custom 1 field description update"
        })
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_custom_fields_unauthorized(self):
        """Test delete custom fields unauthorized"""
        model = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom 1 field description"
        )

        res = self.client.delete(detail_url(model.id))
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenCustomFieldTests(TestCase):
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

    def test_list_custom_fields_forbidden(self):
        """Test list custom fields forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_custom_fields_forbidden(self):
        """Test create custom fields forbidden"""
        payload = {
            "description": "Custom 1 field description",
            "attribute_name": "custom 1", 
            "attribute_slug": "custom1", 
            "attribute_datatype": Attribute.TYPE_TEXT,
        }

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_custom_fields_forbidden(self):
        """Test update custom fields forbidden"""
        model = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom 1 field description"
        )

        res = self.client.patch(detail_url(model.id), {
            'is_active': False,
            'description': "Custom 1 field description update"
        })
        
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


    def test_delete_custom_fields_forbidden(self):
        """Test delete custom fields forbidden"""
        model = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom 1 field description"
        )

        res = self.client.delete(detail_url(model.id))
        
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class CustomFieldTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_customfield')
        aperm = Permission.objects.get(codename='add_customfield')
        cperm = Permission.objects.get(codename='change_customfield')
        dperm = Permission.objects.get(codename='delete_customfield')

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

    def test_list_custom_fields_success(self):
        """Test list custom fields success"""

        models.CustomField.create_custom_field(
                name="custom 2", 
                slug="custom2", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom 2 field description"
        )

        models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom 1 field description"
        )

        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.CustomField.objects.filter(is_active=True).order_by('attribute__name')
        serializer = CustomFieldSerializer(rows, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_create_custom_fields_success(self):
        """Test create custom fields success"""
        payload = {
            "description": "Custom 1 field description",
            "attribute_name": "custom 1", 
            "attribute_slug": "custom1", 
            "attribute_datatype": Attribute.TYPE_TEXT,
        }

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data['description'], payload['description'])
        self.assertEqual(res.data['attribute_name'], payload['attribute_name'])
        self.assertEqual(res.data['attribute_slug'], payload['attribute_slug'])
        self.assertEqual(res.data['attribute_datatype'], payload['attribute_datatype'])

    def test_update_custom_fields_success(self):
        """Test update custom fields success"""
        model = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom 1 field description"
        )

        res = self.client.patch(detail_url(model.id), {
            'is_active': False,
            'description': "Custom 1 field description update"
        })
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['is_active'],  False)
        self.assertEqual(res.data['description'],  "Custom 1 field description update")

    def test_delete_custom_fields_success(self):
        """Test delete custom fields success"""
        model = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom 1 field description"
        )

        res = self.client.delete(detail_url(model.id))
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)