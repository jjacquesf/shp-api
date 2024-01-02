"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models

TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)
    profile_data = {
        "user": user,
        "job_position": "CTO"
    }
    profile = models.Profile.objects.create(**profile_data)
    return user

class PublicUserApiTest(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        user_details = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res =  self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test return error if credentials invalid"""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpassord'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test autentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """Test API requets that require authentication"""

    def setUp(self):
        user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )
        
        self.user = user
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def retrieve_profile_success(self):
        """Test retrieving profile for logged in user success"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_success(self):
        """Test updating the user profile for the authenticated user success"""
        payload = {
            'name': 'Updated name', 
            'password': 'updatedpassword123', 
            "job_position": "CEO", 
            "email": "test@example.com"
        }

        res = self.client.put(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.data["name"], payload['name'])
        if("password" in payload):
            self.assertTrue(self.user.check_password(payload['password']))

        self.assertEqual(res.status_code, status.HTTP_200_OK)