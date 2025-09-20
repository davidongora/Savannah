"""
Pytest configuration and shared fixtures for the Savannah Test Suite
"""
import pytest
import uuid
from django.contrib.auth.models import User
from django.db import connections


@pytest.fixture
def api_client():
    """Provide an API client for testing"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def test_user():
    """Create a test user for authentication"""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Provide an authenticated API client using Django's force_authenticate"""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def test_customer():
    """Create a test customer in the database"""
    with connections['default'].cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO customers (code, name, phone_number) 
            VALUES (%s, %s, %s) 
            RETURNING id
            """,
            ['TESTCUST', 'Test Customer', '+254700000000']
        )
        customer_id = cursor.fetchone()[0]
        
        # Return customer data
        cursor.execute("SELECT * FROM customers WHERE id = %s", [customer_id])
        customer_row = cursor.fetchone()
        
        yield {
            'id': customer_row[0],
            'code': customer_row[1],
            'name': customer_row[2],
            'phone_number': customer_row[3],
            'created_at': customer_row[4],
            'updated_at': customer_row[5]
        }
        
        # Cleanup
        cursor.execute("DELETE FROM customers WHERE id = %s", [customer_id])


@pytest.fixture
def test_order(test_customer):
    """Create a test order in the database"""
    with connections['default'].cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO orders (item, amount, customer_id) 
            VALUES (%s, %s, %s) 
            RETURNING id
            """,
            ['Test Item', 100.00, test_customer['id']]
        )
        order_id = cursor.fetchone()[0]
        
        # Return order data
        cursor.execute("SELECT * FROM orders WHERE id = %s", [order_id])
        order_row = cursor.fetchone()
        
        yield {
            'id': order_row[0],
            'item': order_row[1],
            'amount': float(order_row[2]),
            'customer_id': order_row[3],
            'created_at': order_row[4],
            'updated_at': order_row[5]
        }
        
        # Cleanup
        cursor.execute("DELETE FROM orders WHERE id = %s", [order_id])


@pytest.fixture
def db_connection():
    """Provide database connection for raw SQL tests"""
    return connections['default']


class DatabaseHelper:
    """Helper class for database operations in tests"""
    
    @staticmethod
    def create_customer(code='TESTCUST', name='Test Customer', phone='+254700000000'):
        """Create a customer and return its ID"""
        with connections['default'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customers (code, name, phone_number) 
                VALUES (%s, %s, %s) 
                RETURNING id
                """,
                [code, name, phone]
            )
            return cursor.fetchone()[0]
    
    @staticmethod
    def create_order(item='Test Item', amount=100.00, customer_id=None):
        """Create an order and return its ID"""
        if customer_id is None:
            customer_id = DatabaseHelper.create_customer()
        
        with connections['default'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO orders (item, amount, customer_id) 
                VALUES (%s, %s, %s) 
                RETURNING id
                """,
                [item, amount, customer_id]
            )
            return cursor.fetchone()[0]
    
    @staticmethod
    def cleanup_customers(*codes):
        """Clean up customers by codes"""
        if codes:
            with connections['default'].cursor() as cursor:
                placeholders = ','.join(['%s'] * len(codes))
                cursor.execute(f"DELETE FROM customers WHERE code IN ({placeholders})", codes)
    
    @staticmethod
    def cleanup_orders(*items):
        """Clean up orders by item names"""
        if items:
            with connections['default'].cursor() as cursor:
                placeholders = ','.join(['%s'] * len(items))
                cursor.execute(f"DELETE FROM orders WHERE item IN ({placeholders})", items)
    
    @staticmethod
    def get_customer_by_id(customer_id):
        """Get customer data by ID"""
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT * FROM customers WHERE id = %s", [customer_id])
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'code': row[1],
                    'name': row[2],
                    'phone_number': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            return None
    
    @staticmethod
    def get_order_by_id(order_id):
        """Get order data by ID"""
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE id = %s", [order_id])
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'item': row[1],
                    'amount': float(row[2]),
                    'customer_id': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            return None


@pytest.fixture
def db_helper():
    """Provide database helper for tests"""
    return DatabaseHelper