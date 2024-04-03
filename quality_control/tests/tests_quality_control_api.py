"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from quality_control.serializers import QualityControlSerializer
from permission.views import PermissionQuerySet
# from evidence.serializers import serialize_evidence

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from eav.models import Attribute
from django.contrib.auth.models import Permission

MAIN_URL = reverse('qualitycontrol:qualitycontrol-list')

def detail_url(id):
    return reverse('qualitycontrol:qualitycontrol-detail', args=[id])

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
        
        vperm = Permission.objects.get(codename='view_qualitycontrol')
        aperm = Permission.objects.get(codename='add_qualitycontrol')

        group.permissions.add(vperm)
        group.permissions.add(aperm)

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

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_list_evidence_comment_success(self):
        """Test get all evidence comments success."""
        payload = {
            'name': "My name",
        }
        models.QualityControl.objects.create(**payload)

        res = self.client.get(MAIN_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.QualityControl.objects.filter().order_by('-id')
        s = QualityControlSerializer(rows, many=True)
        self.assertEqual(s.data, res.data)

    def test_evidence_comment_detail_success(self):
        """Test department detail success"""
        payload = {
            'name': "My name"
        }
        model = models.QualityControl.objects.create(**payload)

        res = self.client.get(detail_url(model.id), format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        s = QualityControlSerializer(model)
        self.assertEqual(s.data, res.data)

    def test_create_evidence_comment_success(self):
        """Test create evidence comment success."""
        payload = {
            'name': "My name",
        }


        res = self.client.post(MAIN_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)