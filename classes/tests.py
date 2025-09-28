from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from classes.models import Class

class ClassModelTest(TestCase):
    def setUp(self):
        # Create a superuser and a regular user
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='password'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regularuser@example.com',
            password='password'
        )

    def test_class_creation_by_superuser(self):
        # Test creating a Class instance with a superuser as the owner
        class_instance = Class(
            owner=self.superuser,
            name='Math 101',
            class_code='MATH101',
            description='Introduction to Mathematics'
        )
        class_instance.save()
        self.assertEqual(Class.objects.count(), 1)
        self.assertEqual(class_instance.name, 'Math 101')
        self.assertEqual(class_instance.owner, self.superuser)

    def test_class_creation_by_regular_user_raises_error(self):
        # Test that creating a Class instance with a regular user as the owner raises a ValidationError
        class_instance = Class(
            owner=self.regular_user,
            name='History 101',
            class_code='HIST101',
            description='Introduction to History'
        )
        with self.assertRaises(ValidationError):
            class_instance.save()

    def test_class_code_unique_constraint(self):
        # Test that class_code must be unique
        Class.objects.create(
            owner=self.superuser,
            name='Physics 101',
            class_code='PHYS101',
            description='Introduction to Physics'
        )
        class_instance_duplicate = Class(
            owner=self.superuser,
            name='Advanced Physics',
            class_code='PHYS101',
            description='Advanced topics in Physics'
        )
        with self.assertRaises(ValidationError):
            class_instance_duplicate.full_clean()  # full_clean() should be called to validate uniqueness before saving

    def test_member_list(self):
        # Test adding members to a class
        class_instance = Class.objects.create(
            owner=self.superuser,
            name='Chemistry 101',
            class_code='CHEM101',
            description='Introduction to Chemistry'
        )
        class_instance.member_list.add(self.regular_user)
        self.assertIn(self.regular_user, class_instance.member_list.all())
        self.assertEqual(class_instance.member_list.count(), 1)

