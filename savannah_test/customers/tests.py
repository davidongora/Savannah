import uuid
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connections


class CustomerAPITestCase(APITestCase):
    """Test cases for Customer API endpoints"""
    
    def setUp(self):
        """Set up test data and authentication"""
        self._create_test_tables()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
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
        
        self.customer_data = {
            'code': 'CUST001',
            'name': 'John Doe',
            'phone_number': '+254712345678'
        }
        
        self.test_customer_id = self._create_test_customer()
    
    def _create_test_customer(self):
        """Helper method to create a test customer in the database"""
        import uuid
        customer_id = str(uuid.uuid4())
        with connections['default'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customers (id, code, name, phone_number, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, NOW(), NOW()) 
                RETURNING id
                """,
                [customer_id, 'TESTCUST', 'Test Customer', '+254700000000']
            )
            return cursor.fetchone()[0]
    
    def _cleanup_customers(self):
        """Helper method to clean up test customers"""
        with connections['default'].cursor() as cursor:
            cursor.execute("DELETE FROM customers WHERE code IN ('CUST001', 'TESTCUST', 'UPDATED')")
    
    def tearDown(self):
        """Clean up after each test"""
        self._cleanup_customers()
    
    def test_create_customer_success(self):
        """Test successful customer creation"""
        url = reverse('customer-list')
        response = self.client.post(url, self.customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'CUST001')
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['phone_number'], '+254712345678')
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)
    
    def test_create_customer_missing_required_field(self):
        """Test customer creation with missing required field"""
        incomplete_data = {
            'code': 'CUST002',
            'name': 'Jane Doe'
        }
        url = reverse('customer-list')
        response = self.client.post(url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('phone_number', response.data['error'])
    
    def test_create_customer_duplicate_code(self):
        """Test customer creation with duplicate code"""
        url = reverse('customer-list')
        self.client.post(url, self.customer_data, format='json')
        
        response = self.client.post(url, self.customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('already exists', response.data['error'])
    
    def test_list_customers(self):
        """Test listing all customers"""
        url = reverse('customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)  
        
        customer_codes = [customer['code'] for customer in response.data]
        self.assertIn('TESTCUST', customer_codes)
    
    def test_get_customer_detail(self):
        """Test retrieving a specific customer"""
        url = reverse('customer-detail', args=[self.test_customer_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'TESTCUST')
        self.assertEqual(response.data['name'], 'Test Customer')
        self.assertEqual(response.data['phone_number'], '+254700000000')
    
    def test_get_customer_detail_not_found(self):
        """Test retrieving a non-existent customer"""
        fake_id = str(uuid.uuid4())
        url = reverse('customer-detail', args=[fake_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_update_customer(self):
        """Test updating a customer"""
        update_data = {
            'code': 'UPDATED',
            'name': 'Updated Name',
            'phone_number': '+254711111111'
        }
        url = reverse('customer-detail', args=[self.test_customer_id])
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'UPDATED')
        self.assertEqual(response.data['name'], 'Updated Name')
        self.assertEqual(response.data['phone_number'], '+254711111111')
    
    def test_update_customer_not_found(self):
        """Test updating a non-existent customer"""
        fake_id = str(uuid.uuid4())
        url = reverse('customer-detail', args=[fake_id])
        response = self.client.put(url, self.customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_customer(self):
        """Test deleting a customer"""
        url = reverse('customer-detail', args=[self.test_customer_id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_customer_not_found(self):
        """Test deleting a non-existent customer"""
        fake_id = str(uuid.uuid4())
        url = reverse('customer-detail', args=[fake_id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are rejected"""
        self.client.credentials()
        
        url = reverse('customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerViewTestCase(TestCase):
    """Test cases for Customer view logic without API calls"""
    
    def setUp(self):
        """Set up test database connections and create tables"""
        self.connection = connections['default']
        self._create_test_tables()
    
    def _create_test_tables(self):
        """Create necessary tables for testing"""
        with self.connection.cursor() as cursor:
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
    
    def test_database_connection(self):
        """Test that database connection works"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            result = cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertIn('PostgreSQL', result[0])
    
    def test_customers_table_exists(self):
        """Test that customers table exists and has correct structure"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'customers'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            expected_columns = ['id', 'code', 'name', 'phone_number', 'created_at', 'updated_at']
            actual_columns = [col[0] for col in columns]
            
            for expected_col in expected_columns:
                self.assertIn(expected_col, actual_columns)