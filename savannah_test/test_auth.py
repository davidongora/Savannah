from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import User

class TestAuthentication(BaseAuthentication):
    """
    Simple test authentication that always returns the first user
    """
    def authenticate(self, request):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        return (user, None)
    
    def authenticate_header(self, request):
        return 'Test'