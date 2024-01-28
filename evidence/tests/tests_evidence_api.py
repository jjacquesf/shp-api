"""
Tests for evidence APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from evidence.serializers import (
    EvidenceSerializer
)

MAIN_URL = reverse('evidence:evidence-list')

def detail_url(id):
    return reverse('evidence:evidence-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)


def create_evidence(**params):
    return models.Evidence.objects.create(**params)

class PublicEvidenceTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_evidencies_unauthorized(self):
        """Test list evidencies unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_detail_unauthorized(self):
        """Test evidence detail unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_evidence_unauthorized(self):
        """Test creating a evidence unauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_update_unauthorized(self):
        """Test evidence update unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_partial_update_unauthorized(self):
        """Test evidence partial update unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenEvidenceTests(TestCase):
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

    def test_list_evidencies_forbidden(self):
        """Test list evidencies forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_detail_forbidden(self):
        """Test evidence detail forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_evidence_forbidden(self):
        """Test creating a evidence forbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_update_forbidden(self):
        """Test evidence update forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_partial_update_forbidden(self):
        """Test evidence partial update forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_delete_success(self):
        """Test evidence delete success"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class EvidenceTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_evidence')
        aperm = Permission.objects.get(codename='add_evidence')
        cperm = Permission.objects.get(codename='change_evidence')
        dperm = Permission.objects.get(codename='delete_evidence')

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

    def test_list_active_evidencies_success(self):
        """Test list evidencies success"""
        data = {'name': 'name1', 'level': 0}
        create_evidence(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_evidence(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        
        
        rows = models.Evidence.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_evidencies_success(self):
        """Test list filtered evidencies success"""
        data = {'name': 'name1', 'level': 0}
        create_evidence(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_evidence(**data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Evidence.objects.all().order_by('name')
        serializer = EvidenceSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_evidence_detail_success(self):
        """Test evidence detail success"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Evidence.objects.get(id=model.id)
        serializer = EvidenceSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_evidence_success(self):
        """Test creating a evidence success"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        evidence = models.Evidence.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(evidence, k), v)

        payload.update({'name': 'name4', 'parent': res.data['id']})
        res2 = self.client.post(MAIN_URL, payload)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

        evidence = models.Evidence.objects.get(id=res2.data['id'])
        self.assertEqual(evidence.level, 1)
        for k,v in payload.items():
            if k == 'parent':
                self.assertEqual(getattr(evidence, k).id, v)
            else:
                self.assertEqual(getattr(evidence, k), v)

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

    def test_evidence_update_success(self):
        """Test evidence update success"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Evidence.objects.get(id=model.id)
        serializer = EvidenceSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_evidence_partial_update_success(self):
        """Test evidence partial update success"""
        data = {'name': 'name10', 'level': 0}
        model = create_evidence(**data)
        data = {'name': 'name10'}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Evidence.objects.get(id=model.id)
        serializer = EvidenceSerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_evidence_update_level_not_allowed_success(self):
        """Test evidence partial update level not allowed"""
        org_level = 0
        data = {'name': 'name10', 'level': org_level}
        model = create_evidence(**data)
        data = {'level': 1}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Evidence.objects.get(id=model.id)
        serializer = EvidenceSerializer(rows)
        self.assertEqual(serializer.data['level'], org_level)

    def test_evidence_update_level_not_allowed_success(self):
        """Test evidence partial update level not allowed"""
        org_level = 0
        data = {'name': 'name10', 'level': org_level}
        model = create_evidence(**data)
        data = {'level': 1}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Evidence.objects.get(id=model.id)
        serializer = EvidenceSerializer(rows)
        self.assertEqual(serializer.data['level'], org_level)


    def test_evidence_delete_success(self):
        """Test evidence delete success"""
        data = {'name': 'name1', 'level': 0}
        model = create_evidence(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_evidence_delete_parent_not_allowed(self):
        """Test evidence delete parent not allowed"""
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
