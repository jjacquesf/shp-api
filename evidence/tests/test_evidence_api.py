"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from evidence.serializers import EvidenceSerializer
from permission.views import PermissionQuerySet
# from evidence.serializers import serialize_evidence

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from eav.models import Attribute
from django.contrib.auth.models import Permission

MAIN_URL = reverse('evidence:evidence-list')

def detail_url(id):
    return reverse('evidence:evidence-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)
    profile_data = {
        "user": user,
        "job_position": "CTO"
    }
    profile = models.Profile.objects.create(**profile_data)
    return user

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

def create_evidence_type(**params):
    """Create and return a new evidence status"""
    evidence_type = models.EvidenceType.objects.create(**params)
    return evidence_type

class PublicUserApiTest(TestCase):
    """Test the public features of the user API"""
    pass

class PrivateUserApiTests(TestCase):
    """Test API requets that require authentication"""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='admin')
        
        vperm = Permission.objects.get(codename='view_evidence')
        aperm = Permission.objects.get(codename='add_evidence')
        cperm = Permission.objects.get(codename='change_evidence')

        group.permissions.add(vperm)
        group.permissions.add(aperm)
        group.permissions.add(cperm)

        user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )

        # print("======Assign a group to a user========")
        # user.groups.add(group.pk)
        # print("======Add user to a group========")
        group.user_set.add(user)

        # print("===user group permissions===")
        # print(user.get_group_permissions())
        # print("==============")

        self.user = user

        data = {'name': 'name1', 'position': 1}
        stage = create_evidence_stage(**data)
        self.stage = stage

        data = {'name': 'name1', 'alias': 'name1'}
        egroup = create_evidence_group(**data)
        self.egroup = egroup

        data = {
            'name': 'name1', 
            'position': 1, 
            'color': '#ffffff', 
            'group': self.egroup, 
            'stage': self.stage
        }
        estatus = create_evidence_status(**data)
        self.estatus = estatus

        data = {
            'name': 'name1', 
            'alias': 'name1', 
            'attachment_required': False, 
            'group': self.egroup,
            'description': 'desc1'
        }
        etype = create_evidence_type(**data)
        self.etype = etype

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_evidence_success(self):
        """Test get all evidences success."""
        payload = {
            'type': self.etype,
            'owner': self.user,
            'status': self.estatus,
            'dirty': True,
            'pending_auth': False,
            'pending_signature': False,
            'version': 1,
        }
        models.Evidence.objects.create(**payload)
        res = self.client.get(MAIN_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.Evidence.objects.filter().order_by('-id')
        s = EvidenceSerializer(rows, many=True)
        self.assertEqual(s.data, res.data)

    def test_evidence_detail_success(self):
        """Test department detail success"""
        payload = {
            'type': self.etype,
            'owner': self.user,
            'status': self.estatus,
            'dirty': True,
            'pending_auth': False,
            'pending_signature': False,
            'version': 1,
        }
        model = models.Evidence.objects.create(**payload)

        res = self.client.get(detail_url(model.id), format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        s = EvidenceSerializer(model)
        self.assertEqual(s.data, res.data)
        print(res.data)

    def test_create_evidence_success(self):
        """Test create evidences success."""
        Attribute.objects.create(name='Color', slug='color', datatype=Attribute.TYPE_TEXT)
        Attribute.objects.create(name='Responsable', slug='responsible', datatype=Attribute.TYPE_TEXT)
        payload = {
            'type': self.etype.id,
            'status': self.estatus.id,
            'authorizers': [self.user.id],
            'signers': [self.user.id],
            'eav': '{"color": "#ff0000", "responsible": "Me"}'
        }


        res = self.client.post(MAIN_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_evidence_success(self):
        """Test update evidences success."""
        Attribute.objects.create(name='Color', slug='color', datatype=Attribute.TYPE_TEXT)
        Attribute.objects.create(name='Responsable', slug='responsible', datatype=Attribute.TYPE_TEXT)
        payload = {
            'owner': self.user,
            'type': self.etype,
            'status': self.estatus,
            "eav__color": "#ff0000",
            "eav__responsible": "Me"
        }
        model = models.Evidence.objects.create(**payload)


        data = {
            'status': self.estatus.id,
            'eav': '{"color": "#00ff00", "responsible": "You"}',
        }

        res = self.client.patch(detail_url(model.id), data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)