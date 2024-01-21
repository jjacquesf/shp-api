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
from eav.models import Attribute

from evidence_type.serializers import (
    EvidenceTypeSerializer,
)

from custom_field.serializers import (
    CustomFieldSerializer,
)

MAIN_URL = reverse('evidencetype:evidencetype-list')

def detail_url(id):
    return reverse('evidencetype:evidencetype-detail', args=[id])

def custom_fields_url(id):
    return reverse('evidencetype:custom-fields', args=[id])

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

def create_evidence_type(**params):
    """Create and return a new evidence status"""
    evidence_type = models.EvidenceType.objects.create(**params)
    return evidence_type

class PublicEvidenceTypeTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

        data = {'name': 'name1', 'position': 1}
        stage = create_evidence_stage(**data)
        self.stage = stage

        data = {'name': 'name1', 'alias': 'name1'}
        egroup = create_evidence_group(**data)
        self.egroup = egroup

    def test_list_evidence_type_unauthorized(self):
        """Test list evidence types unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_type_detail_unauthorized(self):
        """Test evidence status detail unauthorized"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_evidence_type_unauthorized(self):
        """Test creating a entity unauthorized"""
        payload = {
            'name': 'name1', 
            'alias': 'name1', 
            'type': 0, 
            'stage': 0,
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_type_update_unauthorized(self):
        """Test evidence status update unauthorized"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_evidence_type_partial_update_unauthorized(self):
        """Test evidence status partial update unauthorized"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_custom_fields_unauthorized(self):
        """Test evidence status partial update unauthorized"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        res = self.client.get(custom_fields_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_custom_fields_unauthorized(self):
        """Test evidence status partial update unauthorized"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        customField = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom field description"
        )

        customField2 = models.CustomField.create_custom_field(
                name="custom 2", 
                slug="custom2", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom field description"
        )

        res = self.client.put(custom_fields_url(model.id), {
            'custom_fields': [customField.id, customField2.id]
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenEvidenceTypeTests(TestCase):
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

        self.client.force_authenticate(user=self.user)

    def test_list_active_evidence_type_forbidden(self):
        """Test list evidence types forbidden"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_evidence_type_forbidden(self):
        """Test creating a entity forbidden"""
        payload = {
            'name': 'name1', 
            'alias': 'name1', 
            'group': self.egroup.id, 
            'stage': self.stage.id
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_type_update_forbidden(self):
        """Test evidence status update forbidden"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_type_partial_update_forbidden(self):
        """Test evidence status partial update forbidden"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_evidence_type_delete_forbidden(self):
        """Test evidence status delete forbidden"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_custom_fields_forbidden(self):
        """Test evidence status partial update forbidden"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        res = self.client.get(custom_fields_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_custom_fields_forbidden(self):
        """Test evidence status partial update forbidden"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        customField = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom field description"
        )

        customField2 = models.CustomField.create_custom_field(
                name="custom 2", 
                slug="custom2", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom field description"
        )

        res = self.client.put(custom_fields_url(model.id), {
            'custom_fields': [customField.id, customField2.id]
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class EvidenceTypeTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_evidencetype')
        aperm = Permission.objects.get(codename='add_evidencetype')
        cperm = Permission.objects.get(codename='change_evidencetype')
        dperm = Permission.objects.get(codename='delete_evidencetype')

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

    def test_list_active_evidence_type_success(self):
        """Test list evidence types success"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        create_evidence_type(**data)
        data.update({'is_active': False, 'name': 'name2', 'alias': 'alias2'})
        create_evidence_type(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        
        
        rows = models.EvidenceType.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceTypeSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_evidence_type_success(self):
        """Test list filtered evidence types success"""
        data = {
            'name': 'name2', 
            'alias': 'name2', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc2'
        }
        create_evidence_type(**data)
        data.update({'is_active': False, 'name': 'name3', 'alias': 'alias3'})
        create_evidence_type(**data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.EvidenceType.objects.all().order_by('name')
        serializer = EvidenceTypeSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_evidence_type_detail_success(self):
        """Test evidence status detail success"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.EvidenceType.objects.get(id=model.id)
        serializer = EvidenceTypeSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_create_evidence_type_success(self):
        """Test creating a entity success"""
        payload = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup.id, 
            'description': 'desc1'
        }

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        entity = models.EvidenceType.objects.get(id=res.data['id'])
        for k,v in payload.items():
            if k == 'group':
                self.assertEqual(getattr(entity, k).id, v)
            elif k == 'stage':
                self.assertEqual(getattr(entity, k).id, v)
            else:
                self.assertEqual(getattr(entity, k), v)

        payload.update({'name': 'name4', 'alias': 'alias4'})
        res2 = self.client.post(MAIN_URL, payload)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

        entity = models.EvidenceType.objects.get(id=res2.data['id'])
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
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup.id, 
            'description': 'desc1'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_evidence_type_update_success(self):
        """Test evidence status update success"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)
        data.update({
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup.id,
            'description': 'desc1'
        })
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.EvidenceType.objects.get(id=model.id)
        serializer = EvidenceTypeSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_evidence_type_partial_update_success(self):
        """Test evidence status partial update success"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)
        data = {'name': 'name10', 'is_active': True}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        row = models.EvidenceType.objects.get(id=model.id)
        serializer = EvidenceTypeSerializer(row)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def test_evidence_type_delete_success(self):
        """Test evidence status delete success"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_evidence_type_delete_bad_request(self):
        """Test evidence status delete bad request"""

        data = {
            'name': 'name2', 
            'alias': 'name2', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc2'
        }
        model = create_evidence_type(**data)

        data2 = {
            'name': 'name3', 
            'alias': 'name3', 
            'attachment_required': False, 
            'group': self.egroup,
            'parent': model,
            'description': 'desc3'
        }
        create_evidence_type(**data2)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_custom_fields_success(self):
        """Test evidence status partial update success"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        customField = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom field description"
        )

        model.custom_fields.add(customField)
        model.save()

        res = self.client.get(custom_fields_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = CustomFieldSerializer(model.custom_fields.all(), many=True)
        self.assertEqual(res.data, serializer.data)

    def test_update_custom_fields_success(self):
        """Test evidence status partial update success"""
        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        model = create_evidence_type(**data)

        customField = models.CustomField.create_custom_field(
                name="custom 1", 
                slug="custom1", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom field description"
        )

        customField2 = models.CustomField.create_custom_field(
                name="custom 2", 
                slug="custom2", 
                datatype=Attribute.TYPE_TEXT,
                description="Custom field description"
        )

        res = self.client.put(custom_fields_url(model.id), {
            'custom_fields': [customField.id, customField2.id]
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = CustomFieldSerializer(model.custom_fields.all(), many=True)
        self.assertEqual(res.data, serializer.data)

