from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.
# Ensure that only PMA Admins can own a Class
# def validate_pma_admin(user):
#     if not user.validate_is_superuser:
#         raise ValidationError("The owner must be a Superuser.")

class Class(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    class_code = models.CharField(max_length=100, unique=True) # Ensure the class_code is unique
    class_id = models.AutoField(primary_key=True) # Auto-generated unique class_id
    description = models.TextField()
    # creation_date = models.DateTimeField(auto_now_add=True)
    member_list = models.ManyToManyField(User, related_name='classes_joined', blank=True)
    pma_admins = models.ManyToManyField(User, related_name='project_pma_admins', blank=True)


    def save(self, *args, **kwargs):
        if not self.owner.is_superuser:
            raise ValidationError("The owner must be a superuser.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name