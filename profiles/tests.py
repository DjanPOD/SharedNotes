from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import Profile

class ProfileModelTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword')
        # Assuming there is a way to mark the user as an admin
        self.admin_user.groups.create(name='PMA Admin')

    def test_profile_creation(self):
        # Delete a profile. 
        Profile.objects.filter(user=self.user).delete()

        # Create a profile and make sure it has been created CORRECTLY!
        profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={"computing_id": "test123", "major": "Computer Science", "year": "Third Year"}
        )
        
        # Checks to see if the profile was created. 
        self.assertTrue(created, "The profile should have been newly created, but it was retrieved instead.")
        self.assertEqual(profile.user, self.user)
