"""
Integration Tests for the Savannah Customer and Order Management System
"""
import pytest
import uuid
from unittest.mock import patch
from django.test import TransactionTestCase
from django.db import connections
from rest_framework import status


@pytest.mark.django_db
class CustomerOrderIntegrationTest:
    """Integration tests for customer and order workflow"""
    
    def test_complete_customer_order_workflow(self, authenticated_client):
        """Test complete workflow: create customer, create order, retrieve data"""
        customer_data = {
            'code': 'WORKFLOW001',
            'name': 'Workflow Test Customer',
            'phone_number': '+254700999888'
        }
        
        response = authenticated_client.post('/api/customers/', customer_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        customer_id = response.data['id']
        assert response.data['code'] == 'WORKFLOW001'
        assert response.data['name'] == 'Workflow Test Customer'
        
        order_data = {
            'item': 'Workflow Test Product',
            'amount': '750.00',
            'customer_id': customer_id
        }
        
        with patch('core.sms_service.send_sms', return_value=True) as mock_sms:
            response = authenticated_client.post('/api/orders/', order_data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            order_id = response.data['id']
            assert response.data['item'] == 'Workflow Test Product'
            assert float(response.data['amount']) == 750.00
            assert response.data['customer_id'] == customer_id
            
            mock_sms.assert_called_once()
        
        response = authenticated_client.get(f'/api/orders/customer/{customer_id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == order_id
        assert response.data[0]['item'] == 'Workflow Test Product'
        
        update_data = {
            'item': 'Updated Workflow Product',
            'amount': '850.00',
            'customer_id': customer_id
        }
        response = authenticated_client.put(f'/api/orders/{order_id}/', update_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['item'] == 'Updated Workflow Product'
        assert float(response.data['amount']) == 850.00
        
        response = authenticated_client.get(f'/api/orders/{order_id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['item'] == 'Updated Workflow Product'
        
        customer_update = {
            'code': 'WORKFLOW001_UPDATED',
            'name': 'Updated Workflow Customer',
            'phone_number': '+254700999777'
        }
        response = authenticated_client.put(f'/api/customers/{customer_id}/', customer_update, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 'WORKFLOW001_UPDATED'
        assert response.data['name'] == 'Updated Workflow Customer'
        
        response = authenticated_client.get(f'/api/orders/customer/{customer_id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['customer_id'] == customer_id
        
        authenticated_client.delete(f'/api/orders/{order_id}/')
        authenticated_client.delete(f'/api/customers/{customer_id}/')
    
    def test_multiple_orders_for_customer(self, authenticated_client, test_customer):
        """Test creating multiple orders for the same customer"""
        customer_id = str(test_customer['id'])
        
        orders_data = [
            {'item': 'Product A', 'amount': '100.00', 'customer_id': customer_id},
            {'item': 'Product B', 'amount': '200.00', 'customer_id': customer_id},
            {'item': 'Product C', 'amount': '300.00', 'customer_id': customer_id}
        ]
        
        created_orders = []
        
        with patch('core.sms_service.send_sms', return_value=True):
            for order_data in orders_data:
                response = authenticated_client.post('/api/orders/', order_data, format='json')
                assert response.status_code == status.HTTP_201_CREATED
                created_orders.append(response.data['id'])
        
        response = authenticated_client.get(f'/api/orders/customer/{customer_id}/')
        assert response.status_code == status.HTTP_200_OK
        
        customer_orders = response.data
        order_items = [order['item'] for order in customer_orders]
        assert 'Product A' in order_items
        assert 'Product B' in order_items
        assert 'Product C' in order_items
        
        for order_id in created_orders:
            authenticated_client.delete(f'/api/orders/{order_id}/')
    
    def test_delete_customer_with_orders_handling(self, authenticated_client):
        """Test behavior when trying to delete a customer with orders"""
        customer_data = {
            'code': 'DELETETEST',
            'name': 'Delete Test Customer',
            'phone_number': '+254700555666'
        }
        response = authenticated_client.post('/api/customers/', customer_data, format='json')
        customer_id = response.data['id']
        
        order_data = {
            'item': 'Delete Test Item',
            'amount': '99.99',
            'customer_id': customer_id
        }
        
        with patch('core.sms_service.send_sms', return_value=True):
            response = authenticated_client.post('/api/orders/', order_data, format='json')
            order_id = response.data['id']
        
        response = authenticated_client.delete(f'/api/customers/{customer_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        response = authenticated_client.get(f'/api/orders/{order_id}/')
        assert response.status_code == status.HTTP_200_OK
        
        authenticated_client.delete(f'/api/orders/{order_id}/')
    
    @patch('core.sms_service.send_sms')
    def test_sms_integration_in_workflow(self, mock_sms, authenticated_client, test_customer):
        """Test SMS service integration throughout the workflow"""
        customer_id = str(test_customer['id'])
        phone_number = test_customer['phone_number']
        
        mock_sms.return_value = True
        
        order_data = {
            'item': 'SMS Test Product',
            'amount': '450.00',
            'customer_id': customer_id
        }
        
        response = authenticated_client.post('/api/orders/', order_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        mock_sms.assert_called_once()
        call_args = mock_sms.call_args
        assert phone_number in str(call_args)
        assert 'SMS Test Product' in str(call_args)
        
        order_id = response.data['id']
        
        mock_sms.reset_mock()
        mock_sms.return_value = False
        
        order_data_2 = {
            'item': 'SMS Fail Test Product',
            'amount': '250.00',
            'customer_id': customer_id
        }
        
        response = authenticated_client.post('/api/orders/', order_data_2, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        mock_sms.assert_called_once()
        
        order_id_2 = response.data['id']
        authenticated_client.delete(f'/api/orders/{order_id}/')
        authenticated_client.delete(f'/api/orders/{order_id_2}/')
    
    def test_error_handling_in_workflow(self, authenticated_client):
        """Test error handling throughout the workflow"""
        fake_customer_id = str(uuid.uuid4())
        order_data = {
            'item': 'Error Test Product',
            'amount': '100.00',
            'customer_id': fake_customer_id
        }
        
        response = authenticated_client.post('/api/orders/', order_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Customer not found' in response.data['error']
        
        customer_data = {
            'code': 'DUPLICATE001',
            'name': 'First Customer',
            'phone_number': '+254700111222'
        }
        
        response = authenticated_client.post('/api/customers/', customer_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        customer_id = response.data['id']
        
        customer_data_2 = {
            'code': 'DUPLICATE001',
            'name': 'Second Customer',
            'phone_number': '+254700111333'
        }
        
        response = authenticated_client.post('/api/customers/', customer_data_2, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already exists' in response.data['error']
        
        authenticated_client.delete(f'/api/customers/{customer_id}/')
    
    def test_authentication_requirements(self, api_client):
        """Test that authentication is required for all endpoints"""
        response = api_client.get('/api/customers/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = api_client.post('/api/customers/', {}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = api_client.get('/api/orders/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = api_client.post('/api/orders/', {}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class DatabaseIntegrityTest(TransactionTestCase):
    """Test database integrity and constraints"""
    
    def setUp(self):
        """Set up test database tables"""
        self._create_test_tables()
    
    def _create_test_tables(self):
        """Create necessary tables for testing"""
        with connections['default'].cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    code VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                    item VARCHAR(200) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    order_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def test_database_schema_integrity(self):
        """Test that database schema is correctly set up"""
        with connections['default'].cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'customers'
                ORDER BY ordinal_position
            """)
            customer_columns = cursor.fetchall()
            
            expected_customer_columns = {
                'id': 'uuid',
                'code': 'character varying',
                'name': 'character varying',
                'phone_number': 'character varying',
                'created_at': 'timestamp with time zone',
                'updated_at': 'timestamp with time zone'
            }
            
            for col_name, col_type, nullable in customer_columns:
                if col_name in expected_customer_columns:
                    assert col_type == expected_customer_columns[col_name]
            
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'orders'
                ORDER BY ordinal_position
            """)
            order_columns = cursor.fetchall()
            
            expected_order_columns = {
                'id': 'uuid',
                'item': 'character varying',
                'amount': 'numeric',
                'customer_id': 'uuid',
                'created_at': 'timestamp with time zone',
                'updated_at': 'timestamp with time zone'
            }
            
            for col_name, col_type, nullable in order_columns:
                if col_name in expected_order_columns:
                    assert col_type == expected_order_columns[col_name]
    
    def test_database_foreign_key_relationships(self):
        """Test foreign key relationships work correctly"""
        import uuid
        from datetime import datetime, timezone
        
        with connections['default'].cursor() as cursor:
            customer_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            cursor.execute(
                "INSERT INTO customers (id, code, name, phone_number, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
                [customer_id, 'FKTEST', 'FK Test Customer', '+254700123456', now, now]
            )
            
            order_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO orders (id, item, amount, customer_id, order_time, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                [order_id, 'FK Test Item', 99.99, customer_id, now, now, now]
            )
            
            cursor.execute(
                """
                SELECT o.id, o.item, c.code, c.name 
                FROM orders o 
                JOIN customers c ON o.customer_id = c.id 
                WHERE o.id = %s
                """,
                [order_id]
            )
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[1], 'FK Test Item')  
            self.assertEqual(result[2], 'FKTEST')       
            self.assertEqual(result[3], 'FK Test Customer')
            
            cursor.execute("""
                SELECT o.item, c.name 
                FROM orders o 
                JOIN customers c ON o.customer_id = c.id 
                WHERE o.id = %s
            """, [order_id])
            
            result = cursor.fetchone()
            assert result[0] == 'FK Test Item'
            assert result[1] == 'FK Test Customer'
            
            cursor.execute("DELETE FROM orders WHERE id = %s", [order_id])
            cursor.execute("DELETE FROM customers WHERE id = %s", [customer_id])