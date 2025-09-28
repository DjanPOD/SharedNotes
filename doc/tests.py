from django.test import TestCase
from django.contrib.auth.models import User
from .models import Document, DocumentComment, Like
from projects.models import Project
from classes.models import Class
from django.core.exceptions import ValidationError

class DocumentModelTest(TestCase):

    def setUp(self):
        # Create test user and project owner
        self.superuser = User.objects.create_superuser(username='superuser', email='superuser@example.com', password='testpassword')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.pma_admin = User.objects.create_user(username='pma_admin', password='pmapass')
        self.project_owner = User.objects.create_user(username='projectowner', password='projectownerpass')

        self.classs = Class.objects.create(
            name= 'Test Class',
            owner= self.superuser
        )
        # Create project with an owner
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.project_owner, # Set the owner of the project
            class_belongs_to= self.classs
        )

        # Create document linked to the project
        self.document = Document.objects.create(
            owner=self.user,
            title='Test Document',
            file='testfile.txt',
            project=self.project
        )

    def test_document_creation(self):
        # Test the document creation
        self.assertEqual(self.document.title, 'Test Document')
        self.assertEqual(self.document.owner, self.user)
        self.assertEqual(self.document.project, self.project)
        self.assertEqual(self.project.class_belongs_to, self.classs)


    def test_document_delete_permission(self):
        # Test that only the document owner or PMA admins can delete the document
        another_user = User.objects.create_user(username='anotheruser', password='anotherpass')

        # Ensure deletion fails for a non-owner, non-admin
        with self.assertRaises(ValidationError):
            self.document.delete(user=another_user)

        # Ensure the document can be deleted by the owner
        self.document.delete(user=self.user)
        self.assertFalse(Document.objects.filter(title='Test Document').exists())


class CommentModelTest(TestCase):

    def setUp(self):
        # Create test user and project owner
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project_owner = User.objects.create_user(username='projectowner', password='ownerpass')
        self.superuser = User.objects.create_superuser(username='superuser', email='superuser@example.com', password='testpassword')

        self.classs = Class.objects.create(
            name= 'Test Class',
            owner= self.superuser
        )

        # Create project with an owner
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.project_owner,  # Set the owner of the project
            class_belongs_to= self.classs
        )

        # Create a document linked to the project
        self.document = Document.objects.create(
            owner=self.user,
            title='Test Document',
            file='testfile.txt',
            project=self.project  # Link the document to the project
        )

        # Create a test comment linked to the document
        self.comment = DocumentComment.objects.create(
            document=self.document,
            author=self.user,
            content='This is a test comment'
        )

    def test_comment_creation(self):
        # Test that the comment is created correctly
        self.assertEqual(self.comment.content, 'This is a test comment')
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.document, self.document)


class LikeModelTest(TestCase):

    def setUp(self):
        # Create test user and project
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project_owner = User.objects.create_user(username='projectowner', password='ownerpass')
        self.superuser = User.objects.create_superuser(username='superuser', email='superuser@example.com', password='testpassword')

        self.classs = Class.objects.create(
            name='Test Class',
            owner=self.superuser
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.project_owner,  # Set the owner of the project
            class_belongs_to=self.classs
        )
        self.document = Document.objects.create(
            owner=self.user,
            title='Test Document',
            file='testfile.txt',
            project=self.project  # Link the document to the project
        )

        # Create a test like
        self.like = Like.objects.create(
            document=self.document,
            user=self.user
        )

    def test_like_creation(self):
        # Test that the like is created correctly
        self.assertEqual(self.like.user, self.user)
        self.assertEqual(self.like.document, self.document)

    def test_like_str(self):
        # Test the string representation of a like
        self.assertEqual(str(self.like), f'{self.user.username} liked {self.document.title}')
