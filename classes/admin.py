from django.contrib import admin
from .models import Class
from django.contrib.auth.models import User

class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'class_code', 'description')
    search_fields = ('name', 'class_code', 'owner__username')
    list_filter = ('owner',)
    filter_horizontal = ('member_list', 'pma_admins')  # Enable selection of multiple users for these fields

    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'class_code', 'description', 'member_list', 'pma_admins')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Validate that the owner is a superuser before saving
        if not obj.owner.is_superuser:
            raise ValidationError("The owner must be a superuser.")
        super().save_model(request, obj, form, change)

admin.site.register(Class, ClassAdmin)
