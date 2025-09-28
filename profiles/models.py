from django.db import models
from django.contrib.auth.models import User
import boto3
from django.conf import settings

# Create your models here.

def upload_to_profile_folder(instance, filename):
    return f'profiles/{instance.user.username}/{filename}'

class Profile(models.Model):
    USER_TYPE_CHOICES = [('Common', 'Common'),
                         ('PMA Admin', 'PMA Admin'),
                         ('Anonymous', 'Anonymous')
                         ]
    
    YEAR_CHOICES = [ ('First Year','First Year'),
                    ('Second Year','Second Year'),
                    ('Third Year','Third Year'),
                    ('Fourth Year','Fourth Year')
                    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    computing_id = models.TextField(max_length=10, unique=True, blank=True, null=True, default=None)
    major = models.TextField(max_length=50, blank=True, null=True)
    year = models.CharField(max_length=15, choices=YEAR_CHOICES, blank=True, null=True)
    user_type = models.CharField(max_length=20, default='Common', choices=USER_TYPE_CHOICES)
    date_joined = models.DateField(auto_now_add=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_pic = models.FileField(upload_to=upload_to_profile_folder, default='profiles/images/testpfp.png')

    def __str__(self):
        return self.user.username

    def delete_file_from_s3(self, file_key):
        """This is a helper method to delete a file from S3."""
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_key
            )
            return True
        except Exception as e:
            print(f"Error deleting file from S3: {e}")
            return False

    def save(self, *args, **kwargs):
        # Check if the profile picture is being updated
        if self.pk:
            old_profile = Profile.objects.get(pk=self.pk)
            if old_profile.profile_pic and self.profile_pic != old_profile.profile_pic:
                # Delete the old profile picture
                self.delete_file_from_s3(old_profile.profile_pic.name)

        super().save(*args, **kwargs)

