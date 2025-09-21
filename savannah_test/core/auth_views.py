from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken
from oauth2_provider import models as oauth2_models
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
import secrets
from datetime import datetime, timedelta
from django.utils import timezone


@api_view(['POST'])
@permission_classes([AllowAny])
def get_test_token(request):
    """
    Get access token for API testing
    POST /api/auth/test-token/
    {
        "username": "testuser",
        "password": "testpass123"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Get or create OAuth2 application
        application = Application.objects.get(name="Savannah OIDC")
        
        # Create access token
        access_token = AccessToken.objects.create(
            user=user,
            application=application,
            token=secrets.token_urlsafe(30),
            expires=timezone.now() + timedelta(hours=1),
            scope='openid profile email'
        )
        
        return Response({
            'access_token': access_token.token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': 'openid profile email',
            'username': user.username,
            'usage': 'Add to API requests: Authorization: Bearer ' + access_token.token
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create token: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def home_view(request):
    """
    Simple home page
    """
    if request.user.is_authenticated:
        return HttpResponse(f"""
        <h1>Welcome to Savannah API</h1>
        <p>Hello, {request.user.username}!</p>
        <p><a href="/api/auth/user/">User Info</a></p>
        <p><a href="/api/customers/">Customers API</a></p>
        <p><a href="/api/orders/">Orders API</a></p>
        <p><a href="/accounts/logout/">Logout</a></p>
        """)
    else:
        return HttpResponse(f"""
        <h1>Welcome to Savannah API</h1>
        <p>You are not authenticated.</p>
        <p><a href="/api/auth/register/">Create Account</a></p>
        <p><a href="/oidc/authenticate/">Login with OIDC</a></p>
        <p><a href="/api/auth/login/">Login Page</a></p>
        """)


@api_view(['GET'])
@permission_classes([AllowAny])
def oidc_login_page(request):
    """
    OIDC login page
    GET /api/auth/login/
    """
    return render(request, 'oidc_login.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def create_user_page(request):
    """
    User registration page
    GET /api/auth/register/
    """
    return render(request, 'create_user.html')


@api_view(['POST'])
@permission_classes([AllowAny])
def setup_oidc_application(request):
    """
    Create OAuth2 application for OIDC
    POST /api/auth/setup-oidc/
    """
    try:
        application, created = Application.objects.get_or_create(
            name="Savannah OIDC",
            defaults={
                'client_type': Application.CLIENT_CONFIDENTIAL,
                'authorization_grant_type': Application.GRANT_AUTHORIZATION_CODE,
                'client_id': 'savannah-client',
                'client_secret': 'savannah-secret',
                'redirect_uris': 'http://185.240.51.176:8003/oidc/callback/\nhttp://185.240.51.176/oidc/callback/\nhttp://localhost:8003/oidc/callback/'
            }
        )
        
        # Update existing application with correct settings
        application.client_id = 'savannah-client'
        application.client_secret = 'savannah-secret'
        application.authorization_grant_type = Application.GRANT_AUTHORIZATION_CODE
        application.client_type = Application.CLIENT_CONFIDENTIAL
        application.redirect_uris = 'http://185.240.51.176:8003/oidc/callback/\nhttp://185.240.51.176/oidc/callback/\nhttp://localhost:8003/oidc/callback/'
        application.save()
        
        return Response({
            'message': 'OIDC application configured successfully',
            'client_id': application.client_id,
            'client_secret': application.client_secret,
            'redirect_uris': application.redirect_uris.split('\n'),
            'authorization_url': f'http://185.240.51.176:8003/o/authorize/',
            'token_url': f'http://185.240.51.176:8003/o/token/',
            'userinfo_url': f'http://185.240.51.176:8003/o/userinfo/',
            'jwks_url': f'http://185.240.51.176:8003/o/.well-known/jwks.json/'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to setup OIDC application: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """
    Create a new user account
    POST /api/auth/create-user/
    {
        "username": "testuser",
        "password": "testpass123", 
        "email": "test@example.com"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'User already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        
        return Response({
            'message': 'User created successfully',
            'user_id': user.id,
            'username': user.username
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create user: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def oidc_info(request):
    """
    Get OIDC configuration info
    GET /api/auth/oidc-info/
    """
    return Response({
        'authorization_endpoint': 'http://185.240.51.176:8003/o/authorize/',
        'token_endpoint': 'http://185.240.51.176:8003/o/token/',
        'userinfo_endpoint': 'http://185.240.51.176:8003/o/userinfo/',
        'jwks_uri': 'http://185.240.51.176:8003/o/.well-known/jwks.json/',
        'issuer': 'http://185.240.51.176:8003',
        'scopes_supported': ['openid', 'profile', 'email'],
        'response_types_supported': ['code'],
        'grant_types_supported': ['authorization_code'],
        'subject_types_supported': ['public']
    })


@api_view(['GET'])
def user_info(request):
    """
    Get current user info (requires OIDC authentication)
    GET /api/auth/user/
    Authorization: Bearer <access-token>
    """
    return Response({
        'user_id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_authenticated': request.user.is_authenticated
    })