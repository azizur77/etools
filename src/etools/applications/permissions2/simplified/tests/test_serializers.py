from django.test import TestCase

from django.core.exceptions import PermissionDenied

from etools.applications.permissions2.simplified.tests.serializers import ParentSerializer


class TestSafeReadOnlySerializerMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.serializer = ParentSerializer(data={'test_field': 'test_data'})
        cls.readonly_serializer = ParentSerializer(data={'test_field': 'test_data'}, read_only=True)

    def test_write_fields(self):
        self.assertNotEqual(self.serializer._writable_fields, [])

    def test_write_fields_readonly(self):
        self.assertEqual(self.readonly_serializer._writable_fields, [])

    def test_validate(self):
        self.assertTrue(self.serializer.is_valid())

    def test_validate_readonly(self):
        with self.assertRaises(PermissionDenied):
            self.readonly_serializer.is_valid()
