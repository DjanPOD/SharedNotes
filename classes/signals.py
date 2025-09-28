from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from classes.models import Class
from profiles.models import Profile  # Import the correct Profile model
from django.contrib.auth.models import User

@receiver(m2m_changed, sender=Class.pma_admins.through)
def update_user_type(sender, instance, action, reverse, pk_set, **kwargs):
    """
    Signal to update user_type when users are added to or removed from the pma_admins field.
    """

    if action in ['post_add', 'post_remove', 'post_clear']:
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            try:
                profile = Profile.objects.get(user=user)  # Correctly fetch the profile
                # Check if the user is still an admin in any class
                is_pma_admin = Class.objects.filter(pma_admins__id=user.id).exists()
                print(f"User {user.username} i_pma_admin: {is_pma_admin}")
                if is_pma_admin:
                    profile.user_type = 'PMA Admin'
                    profile.save()
                elif not is_pma_admin:
                    profile.user_type = 'Common'
                    profile.save()
            except Profile.DoesNotExist:
                print(f"No profile found for user {user.username}")
