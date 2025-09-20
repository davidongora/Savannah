import uuid
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connections


class OrderAPITestCase(APITestCase):
    """Test cases for Order API endpoints"""
    
    def setUp(self):
        """Set up test data and authentication"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        self.test_customer_id = self._create_test_customer()
        
        self.order_data = {
            'item': 'Laptop',
            'amount': '1500.00',
            'customer_id': str(self.test_customer_id)
        }
        
        self.test_order_id = self._create_test_order()
    
    def _create_test_customer(self):
        """Helper method to create a test customer in the database"""
        with connections['default'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customers (code, name, phone_number) 
                VALUES (%s, %s, %s) 
                RETURNING id
                """,
                ['TESTCUST', 'Test Customer', '+254700000000']
            )
            return cursor.fetchone()[0]
    
    def _create_test_order(self):
        """Helper method to create a test order in the database"""
        with connections['default'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO orders (item, amount, customer_id) 
                VALUES (%s, %s, %s) 
                RETURNING id
                """,
                ['Test Item', 100.00, self.test_customer_id]
            )
            return cursor.fetchone()[0]
    
    def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        with connections['default'].cursor() as cursor:
            cursor.execute("DELETE FROM orders WHERE item IN ('Laptop', 'Test Item', 'Updated Item')")
            cursor.execute("DELETE FROM customers WHERE code = 'TESTCUST'")
    
    def tearDown(self):
        """Clean up after each test"""
        self._cleanup_test_data()
    
    @patch('core.sms_service.send_sms')
    def test_create_order_success(self, mock_sms):
        """Test successful order creation with SMS notification"""
        mock_sms.return_value = True
        
        url = reverse('order-list')
        response = self.client.post(url, self.order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['item'], 'Laptop')
        self.assertEqual(float(response.data['amount']), 1500.00)
        self.assertEqual(response.data['customer_id'], str(self.test_customer_id))
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)
        
        mock_sms.assert_called_once()
    
    def test_create_order_missing_required_field(self):
        """Test order creation with missing required field"""
        incomplete_data = {
            'item': 'Phone',
            'amount': '800.00'
            # Missing customer_id
        }
        url = reverse('order-list')
        response = self.client.post(url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('customer_id', response.data['error'])
    
    def test_create_order_invalid_customer(self):
        """Test order creation with non-existent customer"""
        invalid_data = {
            'item': 'Tablet',
            'amount': '300.00',
            'customer_id': str(uuid.uuid4())
        }
        url = reverse('order-list')
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Customer not found', response.data['error'])
    
    def test_create_order_invalid_amount(self):
        """Test order creation with invalid amount"""
        invalid_data = {
            'item': 'Mouse',
            'amount': 'invalid_amount',
            'customer_id': str(self.test_customer_id)
        }
        url = reverse('order-list')
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('amount', response.data['error'])
    
    @patch('core.sms_service.send_sms')
    def test_create_order_sms_failure(self, mock_sms):
        """Test order creation when SMS sending fails"""
        mock_sms.return_value = False
        
        url = reverse('order-list')
        response = self.client.post(url, self.order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['item'], 'Laptop')
        
        mock_sms.assert_called_once()
    
    def test_list_orders(self):
        """Test listing all orders"""
        url = reverse('order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)  
        
        order_items = [order['item'] for order in response.data]
        self.assertIn('Test Item', order_items)
    
    def test_get_order_detail(self):
        """Test retrieving a specific order"""
        url = reverse('order-detail', args=[self.test_order_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item'], 'Test Item')
        self.assertEqual(float(response.data['amount']), 100.00)
        self.assertEqual(response.data['customer_id'], str(self.test_customer_id))
    
    def test_get_order_detail_not_found(self):
        """Test retrieving a non-existent order"""
        fake_id = str(uuid.uuid4())
        url = reverse('order-detail', args=[fake_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_update_order(self):
        """Test updating an order"""
        update_data = {
            'item': 'Updated Item',
            'amount': '250.00',
            'customer_id': str(self.test_customer_id)
        }
        url = reverse('order-detail', args=[self.test_order_id])
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item'], 'Updated Item')
        self.assertEqual(float(response.data['amount']), 250.00)
    
    def test_update_order_not_found(self):
        """Test updating a non-existent order"""
        fake_id = str(uuid.uuid4())
        url = reverse('order-detail', args=[fake_id])
        response = self.client.put(url, self.order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_order(self):
        """Test deleting an order"""
        url = reverse('order-detail', args=[self.test_order_id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_order_not_found(self):
        """Test deleting a non-existent order"""
        fake_id = str(uuid.uuid4())
        url = reverse('order-detail', args=[fake_id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_orders_by_customer(self):
        """Test retrieving orders for a specific customer"""
        url = reverse('orders-by-customer', args=[self.test_customer_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        
        for order in response.data:
            self.assertEqual(order['customer_id'], str(self.test_customer_id))
    
    def test_get_orders_by_customer_not_found(self):
        """Test retrieving orders for a non-existent customer"""
        fake_id = str(uuid.uuid4())
        url = reverse('orders-by-customer', args=[fake_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are rejected"""
        self.client.credentials()
        
        url = reverse('order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SMSServiceTestCase(TestCase):
    """Test cases for SMS service integration"""
    
    def setUp(self):
        """Set up test data"""
        self.test_customer_id = self._create_test_customer()
    
    def _create_test_customer(self):
        """Helper method to create a test customer"""
        with connections['default'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customers (code, name, phone_number) 
                VALUES (%s, %s, %s) 
                RETURNING id
                """,
                ['SMSCUST', 'SMS Customer', '+254700123456']
            )
            return cursor.fetchone()[0]
    
    def _cleanup_test_data(self):
        """Helper method to clean up test data"""
        with connections['default'].cursor() as cursor:
            cursor.execute("DELETE FROM customers WHERE code = 'SMSCUST'")
    
    def tearDown(self):
        """Clean up after each test"""
        self._cleanup_test_data()
    
    @patch('core.sms_service.send_sms')
    def test_sms_service_called_with_correct_params(self, mock_sms):
        """Test that SMS service is called with correct parameters"""
        from core.sms_service import send_sms
        
        mock_sms.return_value = True
        
        result = send_sms('+254700123456', 'Test message')
        
        mock_sms.assert_called_once_with('+254700123456', 'Test message')
        self.assertTrue(result)
    
    @patch('core.sms_service.send_sms')
    def test_sms_service_failure_handling(self, mock_sms):
        """Test SMS service failure handling"""
        from core.sms_service import send_sms
        
        mock_sms.return_value = False
        
        result = send_sms('+254700123456', 'Test message')
        
        mock_sms.assert_called_once()
        self.assertFalse(result)


class OrderViewTestCase(TestCase):
    """Test cases for Order view logic without API calls"""
    
    def setUp(self):
        """Set up test database connections"""
        self.connection = connections['default']
    
    def test_database_connection(self):
        """Test that database connection works"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertIn('PostgreSQL', result[0])
    
    def test_orders_table_exists(self):
        """Test that orders table exists and has correct structure"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'orders'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            expected_columns = ['id', 'item', 'amount', 'customer_id', 'created_at', 'updated_at']
            actual_columns = [col[0] for col in columns]
            
            for expected_col in expected_columns:
                self.assertIn(expected_col, actual_columns)
    
    def test_foreign_key_constraint(self):
        """Test that foreign key constraint exists between orders and customers"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    tc.constraint_name, 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name='orders'
                    AND kcu.column_name='customer_id'
            """)
            foreign_keys = cursor.fetchall()
            
            self.assertGreater(len(foreign_keys), 0)
            fk = foreign_keys[0]
            self.assertEqual(fk[1], 'customer_id')  
            self.assertEqual(fk[2], 'customers')   
            self.assertEqual(fk[3], 'id')        