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

from evidence_stage.serializers import (
    EvidenceStageSerializer,
)

MAIN_URL = reverse('evidence_stage:list')


def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_evidence_stage(**params):
    """Create and return a new evidence stage"""
    evidence_stage = models.EvidenceStage.objects.create(**params)
    return evidence_stage

class PublicEvidenceStageTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_evidence_stagess_unauthorized(self):
        """Test list evidences unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class EvidenceStageTests(TestCase):
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

    def test_list_active_evidence_stages_success(self):
        """Test list evidence stages success"""
        data = {'name': 'name1', 'position': 1}
        create_evidence_stage(**data)
        data.update({'name': 'name2', 'position': 2})
        create_evidence_stage(**data)
        data.update({'is_active': False, 'name': 'name3', 'position': 3})
        create_evidence_stage(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        rows = models.EvidenceStage.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceStageSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)