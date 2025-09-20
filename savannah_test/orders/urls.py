from django.urls import path
from .views import OrderListView, OrderDetailView, OrderByCustomerView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('by-customer/', OrderByCustomerView.as_view(), name='order-by-customer'),
    path('customer/<uuid:customer_id>/', OrderByCustomerView.as_view(), name='orders-by-customer'),
]
