from django.contrib import admin
from .models import Profile
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user_username', 
        'user_first_name', 
        'user_last_name', 
        'user_email', 
        'user_date_joined',
        'year',
        'major', 
        'bio',
        'user_type'
    )

    # Add search functionality for user fields and bio
    readonly_fields = (
        'user_first_name', 
        'user_last_name', 
        'user_email', 
        'user_date_joined',
        'user_type'
    )

    # Custom methods to display fields from the related User model
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'First Name'

    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Last Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_date_joined(self, obj):
        return obj.user.date_joined
    user_date_joined.short_description = 'Date Joined'

# Register ProfileAdmin for the Profile model
admin.site.register(Profile, ProfileAdmin)
