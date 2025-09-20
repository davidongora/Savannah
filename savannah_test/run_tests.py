#!/usr/bin/env python
"""
Test Runner Script for Savannah Customer & Order Management System

This script demonstrates how to run the comprehensive test suite
that has been implemented for the Django application.
"""

import os
import sys
import subprocess
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'savannah_test.settings')

def run_command(command, description):
    """Run a command and display results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Exit Code: {result.returncode}")
    except Exception as e:
        print(f"Error running command: {e}")

def main():
    """Main test runner function"""
    
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("Savannah Test Suite Runner")
    print("=" * 60)
    print("This script runs the comprehensive test suite for the")
    print("Django customer and order management system.")
    print()
    
    python_exe = "C:/Users/Davie/Desktop/savannah/savannah_test/myvenv/Scripts/python.exe"
    
    test_commands = [
        (f"{python_exe} -m pytest customers/tests.py::CustomerViewTestCase::test_database_connection -v",
         "Database Connection Test"),
        
        (f"{python_exe} -m pytest test_urls.py::URLTestCase::test_customer_urls -v",
         "Customer URL Pattern Test"),
        
        (f"{python_exe} -m pytest customers/tests.py::CustomerViewTestCase::test_customers_table_exists -v",
         "Database Schema Validation"),
        
        (f"{python_exe} -m pytest test_integration.py::DatabaseIntegrityTest::test_database_schema_integrity -v",
         "Database Integrity Test"),
        
        (f"{python_exe} -m pytest --collect-only",
         "Test Discovery - Show All Available Tests"),
        
        (f"{python_exe} -m pytest test_urls.py::URLTestCase::test_customer_urls customers/tests.py::CustomerViewTestCase test_integration.py::DatabaseIntegrityTest::test_database_schema_integrity --cov=customers --cov=orders --cov-report=term-missing -v",
         "Working Tests with Coverage Report"),
    ]
    
    for command, description in test_commands:
        run_command(command, description)
        input("\nPress Enter to continue to the next test...")
    
    print("\n" + "="*60)
    print("TEST SUITE SUMMARY")
    print("="*60)
    print("Database connectivity and schema validation")
    print("URL pattern resolution and routing") 
    print("Test infrastructure and configuration")
    print("JWT authentication framework")
    print("PostgreSQL UUID primary key support")
    print("Test fixtures and helper functions")
    print("Customer/Order API tests implemented (need debugging)")
    print("SMS service integration with mocking")
    print("Comprehensive integration test scenarios")
    print()
    print("Next Steps:")
    print("1. Debug API endpoint 500 errors")
    print("2. Fix URL pattern mismatches")
    print("3. Resolve UUID generation in test database")
    print("4. Run full test suite with all tests passing")
    print("5. Add performance and load testing")

if __name__ == "__main__":
    main()