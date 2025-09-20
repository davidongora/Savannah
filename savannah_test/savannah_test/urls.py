from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/customers/', include('customers.urls')),
    path('api/orders/', include('orders.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('oidc/', include('mozilla_django_oidc.urls')),
]
