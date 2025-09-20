from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from django.db import connections
from django.conf import settings

from rest_framework.views import APIView

class CustomerListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_db_connection(self):
        return connections['default']
    
    def get(self, request):
        try:
            query = """
                SELECT id, code, name, phone_number, created_at, updated_at 
                FROM customers 
                ORDER BY created_at DESC
            """
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                customers = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response(customers)
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch customers: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new customer"""
        try:
            data = request.data
            required_fields = ['code', 'name', 'phone_number']
            
            for field in required_fields:
                if field not in data:
                    return Response(
                        {"error": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            check_query = "SELECT id FROM customers WHERE code = %s"
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(check_query, [data['code']])
                existing_customer = cursor.fetchone()
            
            if existing_customer:
                return Response(
                    {"error": "Customer code already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            insert_query = """
                INSERT INTO customers (code, name, phone_number) 
                VALUES (%s, %s, %s) 
                RETURNING id, code, name, phone_number, created_at, updated_at
            """
            
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(insert_query, [data['code'], data['name'], data['phone_number']])
                columns = [col[0] for col in cursor.description]
                customer_row = cursor.fetchone()
                customer = dict(zip(columns, customer_row))
            
            return Response(customer, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to create customer: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomerDetailView(APIView):
    """Retrieve, update or delete a customer"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_db_connection(self):
        """Get database connection using settings configuration"""
        return connections['default']
    
    def get(self, request, pk):
        """Get a specific customer"""
        try:
            query = """
                SELECT id, code, name, phone_number, created_at, updated_at 
                FROM customers 
                WHERE id = %s
            """
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(query, [pk])
                customer_row = cursor.fetchone()
                
                if not customer_row:
                    return Response(
                        {"error": "Customer not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                columns = [col[0] for col in cursor.description]
                customer = dict(zip(columns, customer_row))
            
            return Response(customer)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch customer: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, pk):
        """Update a customer"""
        try:
            data = request.data
            
            check_query = "SELECT id FROM customers WHERE id = %s"
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(check_query, [pk])
                existing_customer = cursor.fetchone()
            
            if not existing_customer:
                return Response(
                    {"error": "Customer not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if 'code' in data:
                code_check_query = "SELECT id FROM customers WHERE code = %s AND id != %s"
                with self.get_db_connection().cursor() as cursor:
                    cursor.execute(code_check_query, [data['code'], pk])
                    code_exists = cursor.fetchone()
                
                if code_exists:
                    return Response(
                        {"error": "Customer code already exists"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            update_fields = []
            update_values = []
            
            for field in ['code', 'name', 'phone_number']:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return Response(
                    {"error": "No fields to update"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            update_values.append(pk)
            
            update_query = f"""
                UPDATE customers 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s 
                RETURNING id, code, name, phone_number, created_at, updated_at
            """
            
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(update_query, update_values)
                columns = [col[0] for col in cursor.description]
                customer_row = cursor.fetchone()
                customer = dict(zip(columns, customer_row))
            return Response(customer)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to update customer: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """Delete a customer"""
        try:
            check_query = "SELECT id FROM customers WHERE id = %s"
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(check_query, [pk])
                existing_customer = cursor.fetchone()
            
            if not existing_customer:
                return Response(
                    {"error": "Customer not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            delete_query = "DELETE FROM customers WHERE id = %s"
            with self.get_db_connection().cursor() as cursor:
                cursor.execute(delete_query, [pk])
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to delete customer: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )