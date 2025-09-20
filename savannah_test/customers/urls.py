from django.urls import path
from .views import CustomerListView, CustomerDetailView

urlpatterns = [
    path('', CustomerListView.as_view(), name='customer-list'),
    path('<uuid:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
]
