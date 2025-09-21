from django.urls import path
from . import auth_views

urlpatterns = [
    path('login/', auth_views.oidc_login_page, name='oidc_login_page'),
    path('register/', auth_views.create_user_page, name='create_user_page'),
    path('create-user/', auth_views.create_user, name='create_user'),
    path('test-token/', auth_views.get_test_token, name='get_test_token'),
    path('setup-oidc/', auth_views.setup_oidc_application, name='setup_oidc'),
    path('oidc-info/', auth_views.oidc_info, name='oidc_info'),
    path('user/', auth_views.user_info, name='user_info'),
]