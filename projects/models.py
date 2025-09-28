from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from classes.models import Class

def validate_common(user, project):
    if user in project.get_all_pma_admins():
        raise ValidationError("The owner must be a PMA Admin.")

class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    project_id = models.AutoField(primary_key=True, null=False)
    class_belongs_to = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    folder_in_s3 = models.CharField(max_length=255, unique=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='project_access', blank=True)
    description = models.TextField(blank=True) 

    def save(self, *args, **kwargs):
        if self.owner in self.class_belongs_to.pma_admins.all():
            raise ValidationError("The owner must be a common user, not a PMA Admin.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_all_pma_admins(self):
        """Return all PMA admins for this project"""
        class_pma_admins = list(self.class_belongs_to.pma_admins.all())  
        return class_pma_admins

    def delete(self, *args, **kwargs):
        user = kwargs.pop('user', None)
    
        # Allow deletion if the user is either the owner or part of PMA admins
        if not user or (user != self.owner and user not in self.get_all_pma_admins()):
            raise ValidationError(f"Only the owner or PMA admins can delete this project. "
                              f"Owner: {self.owner}, User: {user}")
        
        super().delete(*args, **kwargs)


class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Most recent comments first
    
    def save(self, *args, **kwargs):
        if self.owner in self.project.get_all_pma_admins():
            raise ValidationError("The owner must be a common user, not a PMA Admin.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.project.name}'
    

class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'project')  # Ensures no duplicate requests

    def __str__(self):
        return f"{self.user.username} requested to join {self.project.title}"

