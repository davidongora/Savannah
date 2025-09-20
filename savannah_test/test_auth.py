from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import User

class TestAuthentication(BaseAuthentication):
    """
    Simple test authentication that can be disabled for unauthenticated tests
    """
    def authenticate(self, request):
        # Check if test wants to simulate unauthenticated request
        if request.META.get('HTTP_X_DISABLE_AUTH') == 'true':
            return None
            
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