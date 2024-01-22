"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models
from eav.models import Attribute

class ModelTests(TestCase):
      """Test models"""

      def test_create_user_with_email_successful(self):
            """Test creating a user with an email is successful"""
            email = 'test@example.com'
            password = 'testpass123'
            user = get_user_model().objects.create_user(
                  email=email,
                  password=password
            )

            self.assertEqual(user.email, email)
            self.assertTrue(user.check_password(password))

      def test_new_user_email_normalized(self):
            """Test email is normalized for new users."""
            sample_emails = [
                  ['test1@EXAMPLE.com', 'test1@example.com'],
                  ['Test2@Example.com', 'Test2@example.com'],
                  ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
                  ['test4@example.COM', 'test4@example.com'],
            ]

            for email, expected in sample_emails:
                  user = get_user_model().objects.create_user(email, 'sample123')
                  self.assertEqual(user.email, expected)

      def test_new_user_without_email_error(self):
            """Test taht creating an user without an email raises a ValueError"""
            with self.assertRaises(ValueError):
                  get_user_model().objects.create_user('', 'test123')

      def test_create_superuser(self):
            """Test creating a superuser"""
            user = get_user_model().objects.create_superuser(
                  'test@example.com',
                  'test123',
            )

            self.assertTrue(user.is_superuser)
            self.assertTrue(user.is_staff)

      def test_create_municipality(self):
            """Test creating a municipality"""
            name = "Zapopan"
            model = models.Municipality.objects.create(
                  name=name
            )
            self.assertEqual(model.name, name)

      def test_create_entity(self):
            """Test creating a entity"""
            name = "Entity name"
            model = models.Entity.objects.create(
                  name=name
            )
            self.assertEqual(model.name, name)


      def test_create_institution(self):
            name = "Institution name"
            model = models.Institution.objects.create(
                  name=name
            )
            self.assertEqual(model.name, name)

      def test_create_stateorg(self):
            """Test creating a stateorg"""
            name = "Name"
            stateorg = models.StateOrg.objects.create(
                  name=name
            )
            self.assertEqual(stateorg.name, name)

      def test_create_sifuser(self):
            """Test creating a sifuser"""
            stateorg = models.StateOrg.objects.create(name="state org")
            name = "SIF user name"
            model = models.SifUser.objects.create(
                  name=name,
                  stateorg=stateorg
            )
            self.assertEqual(model.name, name)

      def test_create_sianuser(self):
            """Test creating a sianuser"""
            stateorg = models.StateOrg.objects.create(name="state org")
            name = "SIAN user name"
            model = models.SianUser.objects.create(
                  name=name,
                  stateorg=stateorg
            )
            self.assertEqual(model.name, name)


      def test_create_supplier(self):
            """Test creating a supplier"""
            name = "Supplier name"
            model = models.Supplier.objects.create(
                  name=name
            )
            self.assertEqual(model.name, name)

      def test_create_evidence_stage(self):
            """Test creating a stage"""
            name = "Evidence Stage name"
            model = models.EvidenceStage.objects.create(
                  name=name,
                  position=1,
                  description="stage description"
            )
            self.assertEqual(model.name, name)


      def test_create_evidence_status(self):
            """Test creating an evidence status"""

            stage = models.EvidenceStage.objects.create(
                  name="Evidence Stage name",
                  position=1,
                  description="stage description"
            )

            type = models.EvidenceType.objects.create(
                  name="Evidence type name",
                  alias="type",
                  description="Evidence type description"
            )

            name = "Evidence status name"
            model = models.EvidenceStatus.objects.create(
                  name=name,
                  color='#ffffff',
                  position=1,
                  description="evidence status description",
                  stage=stage,
                  type=type,
            )
            self.assertEqual(model.name, name)

      def test_create_evidence_status(self):
            """Test creating a status"""
            group = models.EvidenceGroup.objects.create(
                  name="Test Group",
                  alias="group",
                  description="Group description"
            )
            stage = models.EvidenceStage.objects.create(name="Stage")
            name = "Evidence status name"
            model = models.EvidenceStatus.objects.create(
                  name=name,
                  position=1,
                  description="Status description",
                  color="#ff00aa",
                  stage=stage,
                  group=group,
            )
            self.assertEqual(model.name, name)

      def test_create_evidence_type(self):
            group = models.EvidenceGroup.objects.create(
                  name="Test Group",
                  alias="group",
                  description="Group description"
            )

            model = models.EvidenceType.objects.create(
                  name="Evidence type name",
                  alias="type",
                  description="Evidence type description",
                  group=group,
                  attachment_required=True
            )
            self.assertEqual(model.name, "Evidence type name")

      def test_create_evidence_group(self):
            """Test creating a evidence type"""
            group = models.EvidenceGroup.objects.create(
                  name="Test Group",
                  alias="group",
                  description="Group description"
            )

            model = models.EvidenceType.objects.create(
                  name="Evidence type name",
                  alias="type",
                  description="Evidence type description",
                  group=group,
                  attachment_required=True
            )
            self.assertEqual(model.name, "Evidence type name")


            model2 = models.EvidenceType.objects.create(
                  name="Evidence type name2",
                  alias="type2",
                  description="Evidence type description2",
                  group=group,
                  parent=model,
                  attachment_required=True
            )
            self.assertEqual(model2.name, "Evidence type name2")
            self.assertEqual(model2.group.id, model.id)

      def test_create_eav_attribute(self):
            model = Attribute.objects.create(name='Color', slug='color', datatype=Attribute.TYPE_TEXT)
            exists = Attribute.objects.filter(id=model.id).first()
       
            self.assertEqual(model.id, exists.id)
            self.assertEqual(model.name, exists.name)
            self.assertEqual(model.slug, exists.slug)
            self.assertEqual(model.datatype, exists.datatype)

      def test_create_custom_field(self):
            """Test creating a custom field"""

            group = models.EvidenceGroup.objects.create(
                  name="Test Group",
                  alias="group",
                  description="Group description"
            )

            evidenceType = models.EvidenceType.objects.create(
                  name="Evidence type name",
                  alias="type",
                  description="Evidence type description",
                  group=group,
                  attachment_required=True
            )

            customField = models.CustomField.create_custom_field(
                  name="custom 1", 
                  slug="custom1", 
                  datatype=Attribute.TYPE_TEXT,
                  description="Custom field description"
            )

            evidenceType.custom_fields.add(customField, through_defaults={'mandatory': True})
            evidenceType.save()

            self.assertEqual(customField.is_active, True)
            self.assertEqual(customField.attribute.name, "custom 1")
            self.assertEqual(customField.attribute.slug, "custom1")
            self.assertEqual(customField.attribute.datatype, Attribute.TYPE_TEXT)

            added = evidenceType.custom_fields.filter(id=customField.id).first()
            self.assertEqual(customField.is_active, added.is_active)
            self.assertEqual(customField.attribute.name, added.attribute.name)
            self.assertEqual(customField.attribute.slug, added.attribute.slug)
            self.assertEqual(customField.attribute.datatype, added.attribute.datatype)

            cfields = models.CustomField.objects.all()
