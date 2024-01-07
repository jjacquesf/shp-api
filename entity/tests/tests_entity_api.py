"""
Tests for entity APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from entity.serializers import (
    EntitySerializer
)

MAIN_URL = reverse('entity:entity-list')

def detail_url(id):
    return reverse('entity:entity-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)


def create_entity(**params):
    return models.Entity.objects.create(**params)

class PublicEntityTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_entities_unauthorized(self):
        """Test list entities unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_entity_detail_unauthorized(self):
        """Test entity detail unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_entity_unauthorized(self):
        """Test creating a entity unauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_entity_update_unauthorized(self):
        """Test entity update unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_entity_partial_update_unauthorized(self):
        """Test entity partial update unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenEntityTests(TestCase):
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

    def test_list_entities_forbidden(self):
        """Test list entities forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_entity_detail_forbidden(self):
        """Test entity detail forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_entity_forbidden(self):
        """Test creating a entity forbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_entity_update_forbidden(self):
        """Test entity update forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_entity_partial_update_forbidden(self):
        """Test entity partial update forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_entity_delete_success(self):
        """Test entity delete success"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class EntityTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_entity')
        aperm = Permission.objects.get(codename='add_entity')
        cperm = Permission.objects.get(codename='change_entity')
        dperm = Permission.objects.get(codename='delete_entity')

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

    def test_list_active_entities_success(self):
        """Test list entities success"""
        data = {'name': 'name1', 'level': 0}
        create_entity(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_entity(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        
        
        rows = models.Entity.objects.filter(is_active=True).order_by('name')
        serializer = EntitySerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_entities_success(self):
        """Test list filtered entities success"""
        data = {'name': 'name1', 'level': 0}
        create_entity(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_entity(**data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Entity.objects.all().order_by('name')
        serializer = EntitySerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_entity_detail_success(self):
        """Test entity detail success"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Entity.objects.get(id=model.id)
        serializer = EntitySerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_entity_success(self):
        """Test creating a entity success"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        entity = models.Entity.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(entity, k), v)

        payload.update({'name': 'name4', 'parent': res.data['id']})
        res2 = self.client.post(MAIN_URL, payload)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

        entity = models.Entity.objects.get(id=res2.data['id'])
        self.assertEqual(entity.level, 1)
        for k,v in payload.items():
            if k == 'parent':
                self.assertEqual(getattr(entity, k).id, v)
            else:
                self.assertEqual(getattr(entity, k), v)

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

    def test_entity_update_success(self):
        """Test entity update success"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Entity.objects.get(id=model.id)
        serializer = EntitySerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_entity_partial_update_success(self):
        """Test entity partial update success"""
        data = {'name': 'name10', 'level': 0}
        model = create_entity(**data)
        data = {'name': 'name10'}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Entity.objects.get(id=model.id)
        serializer = EntitySerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_entity_update_level_not_allowed_success(self):
        """Test entity partial update level not allowed"""
        org_level = 0
        data = {'name': 'name10', 'level': org_level}
        model = create_entity(**data)
        data = {'level': 1}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Entity.objects.get(id=model.id)
        serializer = EntitySerializer(rows)
        self.assertEqual(serializer.data['level'], org_level)

    def test_entity_update_level_not_allowed_success(self):
        """Test entity partial update level not allowed"""
        org_level = 0
        data = {'name': 'name10', 'level': org_level}
        model = create_entity(**data)
        data = {'level': 1}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Entity.objects.get(id=model.id)
        serializer = EntitySerializer(rows)
        self.assertEqual(serializer.data['level'], org_level)


    def test_entity_delete_success(self):
        """Test entity delete success"""
        data = {'name': 'name1', 'level': 0}
        model = create_entity(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_entity_delete_parent_not_allowed(self):
        """Test entity delete parent not allowed"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        parent_res = self.client.post(MAIN_URL, payload)
        self.assertEqual(parent_res.status_code, status.HTTP_201_CREATED)

        payload.update({'name': 'name4', 'parent': parent_res.data['id']})
        child_res = self.client.post(MAIN_URL, payload)
        self.assertEqual(child_res.status_code, status.HTTP_201_CREATED)

        res = self.client.delete(detail_url(parent_res.data['id']))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
