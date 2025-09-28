from django.contrib import admin
from .models import Project, ProjectComment, JoinRequest

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'class_belongs_to', 'date_created', 'description')
    readonly_fields = ('name', 'owner', 'class_belongs_to', 'date_created', 'description')  # Prevent modification of auto-generated fields
    list_filter = ('date_created', 'class_belongs_to')  # Filters for easy navigation
    raw_id_fields = ('owner', 'class_belongs_to')  # For faster loading of large foreign key relationships
    filter_horizontal = ('members',)  # For managing ManyToManyField members

@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'author', 'created_at', 'updated_at', 'content')
    list_filter = ('created_at', 'updated_at')  # Filters for comment timestamps
    search_fields = ('project__name', 'author__username', 'content')  # Search bar
    raw_id_fields = ('project', 'author')  # Optimized selection for ForeignKey relationships
    readonly_fields = ('project', 'author', 'created_at', 'updated_at', 'content')  


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'timestamp', 'approved')
    readonly_fields = ('user', 'project', 'timestamp', 'approved')
    list_filter = ('approved', 'timestamp')  # Filters for approval status and timestamp
    search_fields = ('user__username', 'project__name')  # Search bar
    raw_id_fields = ('user', 'project')  # Optimize ForeignKey relationships
