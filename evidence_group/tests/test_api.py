"""
Tests for evidence group APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from evidence_group.serializers import (
    EvidenceGroupSerializer,
)

MAIN_URL = reverse('evidence_group:list')


def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_evidence_group(**params):
    """Create and return a new evidence group"""
    evidence_group = models.EvidenceGroup.objects.create(**params)
    return evidence_group

class PublicEvidenceGroupTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_evidence_groupss_unauthorized(self):
        """Test list evidences unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class EvidenceGroupTests(TestCase):
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

    def test_list_active_evidence_groups_success(self):
        """Test list evidence groups success"""
        data = {'name': 'name1', 'alias': 'name1'}
        create_evidence_group(**data)
        data.update({'name': 'name2', 'alias': 'name2'})
        create_evidence_group(**data)
        data.update({'is_active': False, 'name': 'name3', 'alias': 'name3'})
        create_evidence_group(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        rows = models.EvidenceGroup.objects.filter(is_active=True).order_by('name')
        serializer = EvidenceGroupSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)