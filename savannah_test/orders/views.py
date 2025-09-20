from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connections
from django.conf import settings
from core.sms_service import send_sms_notification

from rest_framework.views import APIView

class OrderListView(APIView):
    """List all orders or create a new order"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_db_connection(self):
        """Get database connection using settings configuration"""
        return connections['default']
    
    def get(self, request):
        """Get all orders with customer details"""
        try:
            query = """
                SELECT 
                    o.id, o.item, o.amount, o.order_time, o.created_at,
                    c.id as customer_id, c.code as customer_code, 
                    c.name as customer_name, c.phone_number as customer_phone
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                ORDER BY o.order_time DESC
            """
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                orders = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response(orders)
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch orders: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new order"""
        try:
            data = request.data
            required_fields = ['customer_code', 'item', 'amount']
            
            for field in required_fields:
                if field not in data:
                    return Response(
                        {"error": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            customer_query = "SELECT id, name, phone_number FROM customers WHERE code = %s"
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(customer_query, [data['customer_code']])
                customer_row = cursor.fetchone()
                
                if not customer_row:
                    return Response(
                        {"error": "Customer not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                columns = [col[0] for col in cursor.description]
                customer = dict(zip(columns, customer_row))
            
            insert_query = """
                INSERT INTO orders (customer_id, item, amount) 
                VALUES (%s, %s, %s) 
                RETURNING id, customer_id, item, amount, order_time, created_at
            """
            
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(insert_query, [customer['id'], data['item'], float(data['amount'])])
                columns = [col[0] for col in cursor.description]
                order_row = cursor.fetchone()
                order = dict(zip(columns, order_row))
            
            order_response = {
                **order,
                'customer_code': data['customer_code'],
                'customer_name': customer['name'],
                'customer_phone': customer['phone_number']
            }
            
            send_sms_notification(order_response)
            
            return Response(order_response, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to create order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderDetailView(APIView):
    """Retrieve or delete an order"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_db_connection(self):
        """Get database connection using settings configuration"""
        return connections['default']
    
    def get(self, request, pk):
        """Get a specific order"""
        try:
            query = """
                SELECT 
                    o.id, o.item, o.amount, o.order_time, o.created_at,
                    c.id as customer_id, c.code as customer_code, 
                    c.name as customer_name, c.phone_number as customer_phone
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE o.id = %s
            """
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(query, [pk])
                order_row = cursor.fetchone()
                
                if not order_row:
                    return Response(
                        {"error": "Order not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                columns = [col[0] for col in cursor.description]
                order = dict(zip(columns, order_row))
            
            return Response(order)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """Delete an order"""
        try:
            check_query = "SELECT id FROM orders WHERE id = %s"
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(check_query, [pk])
                existing_order = cursor.fetchone()
            
            if not existing_order:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            delete_query = "DELETE FROM orders WHERE id = %s"
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(delete_query, [pk])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to delete order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderByCustomerView(APIView):
    """Get orders by customer code"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_db_connection(self):
        """Get database connection using settings configuration"""
        return connections['default']
    
    def get(self, request, customer_id=None):
        """Get orders by customer ID or customer code"""
        try:
            if customer_id:
                customer_query = "SELECT id, code FROM customers WHERE id = %s"
                with self.get_db_connection().cursor() as cursor:
                    cursor.execute(customer_query, [customer_id])
                    customer = cursor.fetchone()
                
                if not customer:
                    return Response(
                        {"error": "Customer not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                orders_query = """
                    SELECT 
                        o.id, o.item, o.amount, o.order_time, o.created_at,
                        c.id as customer_id, c.code as customer_code, 
                        c.name as customer_name, c.phone_number as customer_phone
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE c.id = %s
                    ORDER BY o.order_time DESC
                """
                query_param = customer_id
                
            else:
                customer_code = request.query_params.get('customer_code')
                if not customer_code:
                    return Response(
                        {"error": "customer_code parameter is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                customer_query = "SELECT id FROM customers WHERE code = %s"
                with self.get_db_connection().cursor() as cursor:
                    cursor.execute(customer_query, [customer_code])
                    customer = cursor.fetchone()
                
                if not customer:
                    return Response(
                        {"error": "Customer not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                orders_query = """
                    SELECT 
                        o.id, o.item, o.amount, o.order_time, o.created_at,
                        c.id as customer_id, c.code as customer_code, 
                        c.name as customer_name, c.phone_number as customer_phone
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE c.code = %s
                    ORDER BY o.order_time DESC
                """
                query_param = customer_code
            
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(orders_query, [query_param])
                columns = [col[0] for col in cursor.description]
                orders = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response(orders)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch orders: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )