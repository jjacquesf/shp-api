"""
Tests for state organization APIs
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from core import models 

from state_org.serializers import (
    StateOrgSerializer
)

MAIN_URL = reverse('stateorg:stateorg-list')

def detail_url(id):
    return reverse('stateorg:stateorg-detail', args=[id])

def create_user(**params):
    """Create an return a new user"""
    user = get_user_model().objects.create_user(**params)

    return user

def create_group(**params):
    """Create an return a new group"""
    return models.CustomGroup.objects.create(**params)


def createstate_org(**params):
    return models.StateOrg.objects.create(**params)

class PublicStateOrgTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_entities_unauthorized(self):
        """Test list entities unauthorized"""
        res = self.client.get(MAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def teststate_org_detail_unauthorized(self):
        """Test state organization detail unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_createstate_org_unauthorized(self):
        """Test creating a state organization unauthorized"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def teststate_org_update_unauthorized(self):
        """Test state organization update unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def teststate_org_partial_update_unauthorized(self):
        """Test state organization partial update unauthorized"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class ForbiddenStateOrgTests(TestCase):
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

    def teststate_org_detail_forbidden(self):
        """Test state organization detail forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_createstate_org_forbidden(self):
        """Test creating a state organization forbidden"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def teststate_org_update_forbidden(self):
        """Test state organization update forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def teststate_org_partial_update_forbidden(self):
        """Test state organization partial update forbidden"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)
        data.update({'is_active': False})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def teststate_org_delete_success(self):
        """Test state organization delete success"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StateOrgTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):

        group, created = models.CustomGroup.objects.get_or_create(name='test')
        
        vperm = Permission.objects.get(codename='view_stateorg')
        aperm = Permission.objects.get(codename='add_stateorg')
        cperm = Permission.objects.get(codename='change_stateorg')
        dperm = Permission.objects.get(codename='delete_stateorg')

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
        createstate_org(**data)
        data.update({'is_active': False, 'name': 'name2'})
        createstate_org(**data)

        res = self.client.get(MAIN_URL)
        
        params = {'active_only': 'true'}
        res2 = self.client.get(MAIN_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        
        
        rows = models.StateOrg.objects.filter(is_active=True).order_by('name')
        serializer = StateOrgSerializer(rows, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res2.data, serializer.data)

    def test_list_all_entities_success(self):
        """Test list filtered entities success"""
        data = {'name': 'name1', 'level': 0}
        createstate_org(**data)
        data.update({'is_active': False, 'name': 'name2'})
        createstate_org(**data)
        
        params = {'active_only': 'false'}
        res = self.client.get(MAIN_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.StateOrg.objects.all().order_by('name')
        serializer = StateOrgSerializer(rows, many=True)
        self.assertEqual(res.data, serializer.data)

    def teststate_org_detail_success(self):
        """Test state organization detail success"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)

        res = self.client.get(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.StateOrg.objects.get(id=model.id)
        serializer = StateOrgSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def test_createstate_org_success(self):
        """Test creating a state organization success"""
        payload = {
            'is_active': True,
            'name': 'name3'
        }
        res = self.client.post(MAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        state_org = models.StateOrg.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(state_org, k), v)

        payload.update({'name': 'name4', 'parent': res.data['id']})
        res2 = self.client.post(MAIN_URL, payload)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

        state_org = models.StateOrg.objects.get(id=res2.data['id'])
        self.assertEqual(state_org.level, 1)
        for k,v in payload.items():
            if k == 'parent':
                self.assertEqual(getattr(state_org, k).id, v)
            else:
                self.assertEqual(getattr(state_org, k), v)

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

    def teststate_org_update_success(self):
        """Test state organization update success"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)
        data.update({'is_active': False, 'name': 'name2'})
        res = self.client.put(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.StateOrg.objects.get(id=model.id)
        serializer = StateOrgSerializer(rows)
        self.assertEqual(res.data, serializer.data)

    def teststate_org_partial_update_success(self):
        """Test state organization partial update success"""
        data = {'name': 'name10', 'level': 0}
        model = createstate_org(**data)
        data = {'name': 'name10'}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.StateOrg.objects.get(id=model.id)
        serializer = StateOrgSerializer(rows)
        self.assertEqual(res.data['is_active'], serializer.data['is_active'])

    def teststate_org_update_level_not_allowed_success(self):
        """Test state organization partial update level not allowed"""
        org_level = 0
        data = {'name': 'name10', 'level': org_level}
        model = createstate_org(**data)
        data = {'level': 1}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.StateOrg.objects.get(id=model.id)
        serializer = StateOrgSerializer(rows)
        self.assertEqual(serializer.data['level'], org_level)

    def teststate_org_update_level_not_allowed_success(self):
        """Test state organization partial update level not allowed"""
        org_level = 0
        data = {'name': 'name10', 'level': org_level}
        model = createstate_org(**data)
        data = {'level': 1}
        res = self.client.patch(detail_url(model.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        rows = models.StateOrg.objects.get(id=model.id)
        serializer = StateOrgSerializer(rows)
        self.assertEqual(serializer.data['level'], org_level)


    def teststate_org_delete_success(self):
        """Test state organization delete success"""
        data = {'name': 'name1', 'level': 0}
        model = createstate_org(**data)

        res = self.client.delete(detail_url(model.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def teststate_org_delete_parent_not_allowed(self):
        """Test state organization delete parent not allowed"""
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
