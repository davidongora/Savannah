"""
URL Test Cases for Customer and Order APIs
"""
import pytest
from django.urls import reverse, resolve
from django.test import TestCase


class URLTestCase(TestCase):
    """Test URL routing and reverse resolution"""
    
    def test_customer_urls(self):
        """Test customer URL patterns"""
        url = reverse('customer-list')
        self.assertEqual(url, '/api/customers/')
        
        resolved = resolve('/api/customers/')
        self.assertEqual(resolved.view_name, 'customer-list')
        
        test_id = '550e8400-e29b-41d4-a716-446655440000'
        url = reverse('customer-detail', args=[test_id])
        self.assertEqual(url, f'/api/customers/{test_id}/')
        
        resolved = resolve(f'/api/customers/{test_id}/')
        self.assertEqual(resolved.view_name, 'customer-detail')
        self.assertEqual(str(resolved.kwargs['pk']), test_id)
    
    def test_order_urls(self):
        """Test order URL patterns"""
        url = reverse('order-list')
        self.assertEqual(url, '/api/orders/')
        
        resolved = resolve('/api/orders/')
        self.assertEqual(resolved.view_name, 'order-list')
        
        test_id = '550e8400-e29b-41d4-a716-446655440000'
        url = reverse('order-detail', args=[test_id])
        self.assertEqual(url, f'/api/orders/{test_id}/')
        
        resolved = resolve(f'/api/orders/{test_id}/')
        self.assertEqual(resolved.view_name, 'order-detail')
        self.assertEqual(str(resolved.kwargs['pk']), test_id)
    
    def test_orders_by_customer_url(self):
        """Test orders by customer URL pattern"""
        test_customer_id = '550e8400-e29b-41d4-a716-446655440000'
        url = reverse('orders-by-customer', args=[test_customer_id])
        self.assertEqual(url, f'/api/orders/customer/{test_customer_id}/')
        
        resolved = resolve(f'/api/orders/customer/{test_customer_id}/')
        self.assertEqual(resolved.view_name, 'orders-by-customer')
        self.assertEqual(str(resolved.kwargs['customer_id']), test_customer_id)
    
    def test_oidc_urls(self):
        """Test OIDC authentication URLs"""
        # Test OAuth2 provider URLs
        resolved = resolve('/o/')
        self.assertEqual(resolved.namespace, 'oauth2_provider')
        
        # Test OIDC URLs  
        resolved = resolve('/oidc/')
        # OIDC URLs are included but may not have a specific namespace
    
    def test_admin_url(self):
        """Test admin URL"""
        resolved = resolve('/admin/')
        self.assertEqual(resolved.view_name, 'admin:index')


@pytest.mark.django_db
class URLIntegrationTestCase:
    """Integration tests for URL patterns with database"""
    
    def test_customer_crud_urls_work_end_to_end(self, authenticated_client, db_helper):
        """Test that customer CRUD URLs work end-to-end"""
        customer_data = {
            'code': 'URLTEST001',
            'name': 'URL Test Customer',
            'phone_number': '+254700111222'
        }
        
        url = reverse('customer-list')
        response = authenticated_client.post(url, customer_data, format='json')
        assert response.status_code == 201
        
        customer_id = response.data['id']
        
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert any(c['id'] == customer_id for c in response.data)
        
        detail_url = reverse('customer-detail', args=[customer_id])
        response = authenticated_client.get(detail_url)
        assert response.status_code == 200
        assert response.data['code'] == 'URLTEST001'
        
        update_data = {
            'code': 'URLTEST001_UPDATED',
            'name': 'Updated URL Test Customer',
            'phone_number': '+254700111333'
        }
        response = authenticated_client.put(detail_url, update_data, format='json')
        assert response.status_code == 200
        assert response.data['code'] == 'URLTEST001_UPDATED'
        
        response = authenticated_client.delete(detail_url)
        assert response.status_code == 204
        
        response = authenticated_client.get(detail_url)
        assert response.status_code == 404
    
    def test_order_crud_urls_work_end_to_end(self, authenticated_client, test_customer):
        """Test that order CRUD URLs work end-to-end"""
        order_data = {
            'item': 'URL Test Item',
            'amount': '299.99',
            'customer_id': str(test_customer['id'])
        }
        
        url = reverse('order-list')
        with pytest.mock.patch('core.sms_service.send_sms', return_value=True):
            response = authenticated_client.post(url, order_data, format='json')
        assert response.status_code == 201
        
        order_id = response.data['id']
        
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert any(o['id'] == order_id for o in response.data)
        
        detail_url = reverse('order-detail', args=[order_id])
        response = authenticated_client.get(detail_url)
        assert response.status_code == 200
        assert response.data['item'] == 'URL Test Item'
        
        customer_orders_url = reverse('orders-by-customer', args=[test_customer['id']])
        response = authenticated_client.get(customer_orders_url)
        assert response.status_code == 200
        assert any(o['id'] == order_id for o in response.data)
        
        update_data = {
            'item': 'Updated URL Test Item',
            'amount': '399.99',
            'customer_id': str(test_customer['id'])
        }
        response = authenticated_client.put(detail_url, update_data, format='json')
        assert response.status_code == 200
        assert response.data['item'] == 'Updated URL Test Item'
        
        response = authenticated_client.delete(detail_url)
        assert response.status_code == 204
        
        response = authenticated_client.get(detail_url)
        assert response.status_code == 404