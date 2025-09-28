from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from projects.models import Project
from classes.models import Class
from django.conf import settings
import boto3

def upload_to_project_folder(instance, filename):
    # instance.project gives access to the project this document belongs to
    return f'documents/project-{instance.project.project_id}/{filename}' # {instance.project.project_i}

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.lower().strip()

class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to_project_folder)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, help_text="Describe the contents of this file")
    # class_name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    tags = models.ManyToManyField(Tag, related_name='documents', blank=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    due_date = models.DateField(null=True, blank=True, help_text="Optional: Is there a due date for this document?")
    liked_by = models.ManyToManyField(User, through='Like', related_name='liked_documents_set')

    def __str__(self):
        return self.title

    def get_tags_list(self):
        return self.tags.all()
    

    def delete_file_from_s3(self):
        """This is a helper method to delete file from S3"""
        try:
            s3 = boto3.client('s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=self.file.name
            )
            return True
        except Exception as e:
            print(f"Error deleting file from S3: {e}")
            return False

    def delete(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if not user or (user != self.owner and user not in self.project.get_all_pma_admins()):
            raise ValidationError("Only the document owner or PMA admins can delete this document.")
        
        # Delete the file from S3 first
        self.delete_file_from_s3()
        
        # Then delete the model instance
        super().delete(*args, **kwargs)
    
    def is_liked_by(self, user):
        return self.liked_by_users.filter(user=user).exists()

    def toggle_like(self, user):
        like, created = Like.objects.get_or_create(document=self, user=user)
        if not created:  # If the like already existed
            like.delete()  # Remove the like
            self.likes -= 1
            self.save()
            return False  # Indicates the document was unliked
        else:  # If this is a new like
            self.likes += 1
            self.save()
            return True  # Indicates the document was liked

class DocumentComment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.document.title}'
    
    def save(self, *args, **kwargs):
        if self.author.groups.filter(name='PMA Admin').exists():
            raise ValidationError("The owner must be a common user, not a PMA Admin.")
        super().save(*args, **kwargs)

class Like(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='liked_by_users') 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_liked = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} liked {self.document.title}'