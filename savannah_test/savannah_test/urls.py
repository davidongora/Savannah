from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.auth_views import home_view

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/auth/', include('core.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/orders/', include('orders.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('oidc/', include('mozilla_django_oidc.urls')),
]
