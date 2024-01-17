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

from evidence_status.serializers import (
    EvidenceStatusSerializer
)

MAIN_URL = reverse('evidencestatus:evidencestatus-list')

def detail_url(id):
    return reverse('evidencestatus:evidencestatus-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)

def create_evidence_stage(**params):
    """Create and return a new evidence stage"""
    evidence_stage = models.EvidenceStage.objects.create(**params)
    return evidence_stage

def create_evidence_group(**params):
    """Create and return a new evidence group"""
    evidence_group = models.EvidenceGroup.objects.create(**params)
    return evidence_group

def create_evidence_status(**params):
    """Create and return a new evidence status"""
    evidence_status = models.EvidenceStatus.objects.create(**params)
    return evidence_status

class PublicEvidenceStatusTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

        data = {'name': 'name1', 'position': 1}
        stage = create_evidence_stage(**data)
        self.stage = stage

        data = {'name': 'name1', 'alias': 'name1'}
        egroup = create_evidence_group(**data)
        self.egroup = egroup

    def test_list_evidence_status_unauthorized(self):
        """Test list evidence statuses unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_status_detail_unauthorized(self):
        """Test evidence status detail unauthorized"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        model = create_evidence_status(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_evidence_status_unauthorized(self):
        """Test creating a entity unauthorized"""
        payload = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'type': 0, 
            'stage': 0,
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_status_update_unauthorized(self):
        """Test evidence status update unauthorized"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        model = create_evidence_status(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_status_partial_update_unauthorized(self):
        """Test evidence status partial update unauthorized"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        model = create_evidence_status(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenEvidenceStatusTests(TestCase):
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

        data = {'name': 'name1', 'position': 1}
        stage = create_evidence_stage(**data)
        self.stage = stage

        data = {'name': 'name1', 'alias': 'name1'}
        egroup = create_evidence_group(**data)
        self.egroup = egroup

        # data = {
        #     'name': 'name1', 
        #     'position': 1, 
        #     'color': '#ffffff', 
        #     'group': self.egroup, 
        #     'stage': self.stage
        # }
        # status = create_evidence_status(**data)
        # self.status = status

        self.client.force_authenticate(user=self.user)

    def test_create_evidence_status_forbidden(self):
        """Test creating a entity forbidden"""
        payload = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup.id, 
            'stage': self.stage.id
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_status_update_forbidden(self):
        """Test evidence status update forbidden"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        model = create_evidence_status(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_status_partial_update_forbidden(self):
        """Test evidence status partial update forbidden"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        model = create_evidence_status(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_status_delete_success(self):
        """Test evidence status delete success"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        model = create_evidence_status(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class EvidenceStatusTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_evidencestatus')
        aperm = Permission.objects.get(codename='add_evidencestatus')
        cperm = Permission.objects.get(codename='change_evidencestatus')
        dperm = Permission.objects.get(codename='delete_evidencestatus')

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

        data = {'name': 'name1', 'position': 1}
        stage = create_evidence_stage(**data)
        self.stage = stage

        data = {'name': 'name1', 'alias': 'name1'}
        egroup = create_evidence_group(**data)
        self.egroup = egroup

        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_list_active_evidence_status_success(self):
        """Test list evidence statuses success"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        create_evidence_status(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_evidence_status(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        
        
        rows = models.EvidenceStatus.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceStatusSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_evidence_status_success(self):
        """Test list filtered evidence statuses success"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        create_evidence_status(**data)
        data.update({'is_active': False, 'name': 'name2'})
        create_evidence_status(**data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.EvidenceStatus.objects.all().order_by('name')
        serializer = EvidenceStatusSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_evidence_status_detail_success(self):
        """Test evidence status detail success"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        model = create_evidence_status(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.EvidenceStatus.objects.get(id=model.id)
        serializer = EvidenceStatusSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_evidence_status_success(self):
        """Test creating a entity success"""
        payload = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup.id, 
            'stage': self.stage.id,
        }

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        entity = models.EvidenceStatus.objects.get(id=res.data['id'])
        for k,v in payload.items():
            if k == 'group':
                self.assertEqual(getattr(entity, k).id, v)
            elif k == 'stage':
                self.assertEqual(getattr(entity, k).id, v)
            else:
                self.assertEqual(getattr(entity, k), v)

        payload.update({'name': 'name4'})
        res2 = self.client.post(MAIN_URL, payload)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

        entity = models.EvidenceStatus.objects.get(id=res2.data['id'])
        for k,v in payload.items():
            if k == 'group':
                self.assertEqual(getattr(entity, k).id, v)
            elif k == 'stage':
                self.assertEqual(getattr(entity, k).id, v)
            else:
                self.assertEqual(getattr(entity, k), v)

    def test_fail_creation_on_duplicated_name(self):
        """Test fail creation on duplicated name"""
        payload = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup.id, 
            'stage': self.stage.id,
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_evidence_status_update_success(self):
        """Test evidence status update success"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage,
        }
        model = create_evidence_status(**data)
        data.update({
            'is_active': False, 
            'name': 'name2',
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup.id, 
            'stage': self.stage.id,
        })
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.EvidenceStatus.objects.get(id=model.id)
        serializer = EvidenceStatusSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_evidence_status_partial_update_success(self):
        """Test evidence status partial update success"""
        data = {
            'is_active': False,
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage,
        }
        model = create_evidence_status(**data)
        data = {'name': 'name10', 'is_active': True}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        row = models.EvidenceStatus.objects.get(id=model.id)
        serializer = EvidenceStatusSerializer(row)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])


    def test_evidence_status_delete_success(self):
        """Test evidence status delete success"""
        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage,
        }
        model = create_evidence_status(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
