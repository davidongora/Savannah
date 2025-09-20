"""
OpenID Connect authentication backend for Savannah API
"""
import logging
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class SavannahOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """Custom OIDC Authentication Backend for Savannah API"""
    
    def create_user(self, claims):
        """Create a new user from OIDC claims"""
        user = self.UserModel.objects.create_user(
            username=self.get_username(claims),
            email=claims.get('email', ''),
            first_name=claims.get('given_name', ''),
            last_name=claims.get('family_name', ''),
        )
        
        logger.info(f"Created new user {user.username} from OIDC claims")
        
        return user
    
    def update_user(self, user, claims):
        """Update existing user with fresh claims from OIDC"""
        user.email = claims.get('email', user.email)
        user.first_name = claims.get('given_name', user.first_name)
        user.last_name = claims.get('family_name', user.last_name)
        user.save()
        
        logger.info(f"Updated user {user.username} with fresh OIDC claims")
        
        return user
    
    def get_username(self, claims):
        """Generate username from claims"""
        username = claims.get('preferred_username')
        if not username:
            username = claims.get('email', '').split('@')[0]
        if not username:
            username = claims.get('sub', '')
        
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1
            
        return username
    
    def verify_claims(self, claims):
        """Verify that the claims contain required information"""
        required_claims = ['sub']
        for claim in required_claims:
            if claim not in claims:
                logger.warning(f"Missing required claim: {claim}")
                return False
        
        return True
    
    def filter_users_by_claims(self, claims):
        """Filter users by OIDC claims"""
        sub = claims.get('sub')
        if not sub:
            return self.UserModel.objects.none()
        
        username = self.get_username(claims)
        try:
            return self.UserModel.objects.filter(username=username)
        except self.UserModel.DoesNotExist:
            return self.UserModel.objects.none()


class OIDCBearerTokenAuthentication:
    """
    Custom authentication class for OIDC Bearer tokens in DRF
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token)
        """
        from mozilla_django_oidc.contrib.drf import OIDCAuthentication
        
        oidc_auth = OIDCAuthentication()
        return oidc_auth.authenticate(request)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'Bearer realm="api"'