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

from core import models 
from eav.models import Attribute


# from custom_field.serializers import (
#     CustomFieldSerializer
# )

# MAIN_URL = reverse('customfield:customfield-list')

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

    def test_custom_attrs(self):
        """Test demo"""
        attr = Attribute.objects.create(name='Color', slug='color', datatype=Attribute.TYPE_TEXT)
        attr2 = Attribute.objects.create(name='Type', slug='type', datatype=Attribute.TYPE_TEXT)

        attrv = 'color'
        data = {'name': 'name1', 'alias': 'name1', f'eav__{attrv}': 'red'}
        model = models.EvidenceGroup.objects.create(**data)

        data2 = {'name': 'name2', 'alias': 'name2', 'eav__type': 'specific'}
        model2 = models.EvidenceGroup.objects.create(**data2)
        print('====')
        print('====')
        print('====')
        print(model.eav_values.all())
        print('====')
        print('====')
        print(model2.eav_values.all())
        print('====')
        print('====')
        # found = Attribute.objects.filter(slug='color')
        # print('found')
        # print(found[0])
        # print('====')
        # print('====')


# class ForbiddenCustomFieldTests(TestCase):
#     """Test unauthenticated API requests."""

#     def setUp(self):
#         self.client = APIClient()

#         user_data = {
#             'name': 'test name',
#             'email': 'test@example.com',
#             'password': 'test-user-password123',
#         }

#         user = create_user(**user_data)
#         self.user = user

# class CustomFieldTests(TestCase):
#     """Test unauthenticated API requests."""

#     def setUp(self):

#         group, created = models.CustomGroup.objects.get_or_create(name='test')
        
#         vperm = Permission.objects.get(codename='view_customfield')
#         aperm = Permission.objects.get(codename='add_customfield')
#         cperm = Permission.objects.get(codename='change_customfield')
#         dperm = Permission.objects.get(codename='delete_customfield')

#         group.permissions.add(vperm)
#         group.permissions.add(aperm)
#         group.permissions.add(cperm)
#         group.permissions.add(dperm)

#         user = create_user(
#             email='test@example.com',
#             password='testpass123',
#             name='Test Name',
#         )

#         # print("======Assign a group to a user========")
#         # user.groups.add(group.pk)
#         # print("======Add user to a group========")
#         group.user_set.add(user)

#         # print("===user group permissions===")
#         # print(user.get_group_permissions())
#         # print("==============")


#         # content_type = ContentType.objects.get_for_model(get_user_model())
#         # content_type2 = ContentType.objects.get_for_model(models.CustomGroup)
#         # user_permission = Permission.objects.filter(Q(content_type=content_type) | Q(content_type=content_type2))
#         # print(user_permission)

#         self.group = group

#         self.client = APIClient()
#         self.client.force_authenticate(user=user)
