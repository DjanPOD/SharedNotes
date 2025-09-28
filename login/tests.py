from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

class LoginViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login:login')  # Updated to match the name in your URL configuration
        self.auth_receiver_url = reverse('login:auth_receiver')
        self.logout_url = reverse('login:logout')
        self.anonymous_login_url = reverse('login:anonymous_login')

    # Purpose: verifies that a user can successfully authenticate with a valid Google token. 
    # This is done by mocking the verify_oauth2_token function to simulate a valid token
    # Response status code will be 302 which maens a successful redirect. 
    # Implies that the user with the given email now exists in the database.
    @patch.dict('os.environ', {'GOOGLE_OAUTH_CLIENT_ID': 'fake_google_client_id'})
    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_auth_receiver_valid_token(self, mock_verify_oauth2_token):
        mock_verify_oauth2_token.return_value = {
            'email': 'testuser@example.com',
            'given_name': 'Test',
            'family_name': 'User'
        }

        # Simulate a POST request with a valid token
        response = self.client.post(self.auth_receiver_url, {'credential': 'valid_token'})

        # Check if the user was created and redirected correctly
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())

    #  Purpose: Ensures that invalid tokens are handled correctly by the authentication system. 
    #  The point is to mock the veriffy_oauth2_token function and to raise a ValueError. This would simulate what would happen if an invalid token was provided. 
    #  A POST request is sent to auth_receiver which will respond with status code 403 indicating that the the authentication failed!
    @patch.dict('os.environ', {'GOOGLE_OAUTH_CLIENT_ID': 'fake_google_client_id'})
    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_auth_receiver_invalid_token(self, mock_verify_oauth2_token):
        mock_verify_oauth2_token.side_effect = ValueError()
        response = self.client.post(self.auth_receiver_url, {'credential': 'invalid_token'})
        self.assertEqual(response.status_code, 403)

    # Purpose: to test that an authenticated user can access their information correctly. 
    # Creates a test user and then logs them in with already made up data. 
    # Afterwards, a GET request to the user_info view to see if the response status code is 200 or not. Indicating that the page loaded the correctly. 
    # Furthermore, asserts that the response contains the correct user's email. Which should be testuser@example.com. 
    def test_user_info_authenticated(self):
        user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password')
        self.client.login(username='testuser', password='password')

        session = self.client.session
        session['user_data'] = {'email': user.email, 'first_name': 'Test', 'last_name': 'User'}
        session.save()

        response = self.client.get(reverse('login:user_info'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser@example.com')

    # Purpose: Ensures that unauthenticated users are unable to access the user info page. 
    # Essentially, asking, "Hey user_info view, I want to see if I am a test user!" 
    # This test wants to respond "No you are not by responding with the code 403." which indiates that the user is unauthorized. 
    # Big picture: we are testing this function: def user_info(request):
    def test_user_info_unauthenticated(self):
        response = self.client.get(reverse('login:user_info'))
        self.assertEqual(response.status_code, 403)

    # Purpose: Verifies the functionality of logging out a user. 
    # Creates test user and logs them into the system. 
    # Afterwards, the test client/test user asks/GET request to logout via a URL. 
    # Then the test makes sure that the response, from the request, reidrects to the home page screen WITHOUT containing the key of _auth_user_id which asserts that the user has successfully logged out. 
    def test_log_out(self):
        user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password')
        self.client.login(username='testuser', password='password')

        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    # Purpose: The test_anonymous_login checks that a guest user can successfully log in using the anonymous_login view. 
    # First part of the test is, the test client asks, "hey view, am I good to checkout the app?" If the view responds with 302, then redirects the user to a screen that is fit for an anonymous user.  
    # Second part of the test is to see if the guest user username is already being used. The purpose for this is to find duplicates.
    # More specifically, "hey view, does there exist another like me?" 
    def test_anonymous_login(self):
        # Test logging in as a guest
        response = self.client.get(self.anonymous_login_url)
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertTrue(User.objects.filter(username='guest').exists())

        response = self.client.get(self.anonymous_login_url)
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertEqual(User.objects.filter(username='guest').count(), 1)