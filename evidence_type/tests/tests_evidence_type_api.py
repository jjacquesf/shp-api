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

from evidence_type.serializers import (
    EvidenceTypeSerializer,
)

MAIN_URL = reverse('evidence_type:list')


def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_evidence_type(**params):
    """Create and return a new evidence type"""
    evidence_type = models.EvidenceType.objects.create(**params)
    return evidence_type

class PublicEvidenceTypeTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_evidence_typess_unauthorized(self):
        """Test list evidences unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class EvidenceTypeTests(TestCase):
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

    def test_list_active_evidence_types_success(self):
        """Test list evidence types success"""
        data = {'name': 'name1', 'alias': 'name1'}
        create_evidence_type(**data)
        data.update({'name': 'name2', 'alias': 'name2'})
        create_evidence_type(**data)
        data.update({'is_active': False, 'name': 'name3', 'alias': 'name3'})
        create_evidence_type(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        rows = models.EvidenceType.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceTypeSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)