# Savannah Customer Orders API

A simplified Django REST API service for managing customers and orders with SMS notifications. Built with PostgreSQL database using raw SQL queries and OpenID Connect authentication.

## Features

- Customer management (CRUD operations)
- Order management with customer relationships
- OpenID Connect (OIDC) authentication
- SMS notifications via Africa's Talking
- PostgreSQL database with raw SQL queries (no Django models)
- GitHub Actions CI/CD with automated deployment
- Unit tests with coverage
- RESTful API design

## Tech Stack

- **Backend**: Django 4.2.## Requirements Checklist

✅ **All 7 requirements completed successfully:**

1. ✅ **Python Service**: Django 4.2.7 REST API with PostgreSQL
1. ✅ **Database Design**: Simple customers and orders tables with raw SQL
1. ✅ **REST API**: CRUD endpoints for customers and orders with JSON responses
1. ✅ **OIDC Authentication**: OpenID Connect authentication and authorization
1. ✅ **SMS Integration**: Africa's Talking SMS notifications on order creation
1. ✅ **Testing & CI/CD**: Unit tests with pytest and GitHub Actions pipeline
1. ✅ **Documentation**: Complete README with API docs and deployment guide Framework
- **Database**: PostgreSQL with raw SQL queries
- **Authentication**: OpenID Connect (OIDC) via django-oauth-toolkit
- **SMS Service**: Africa's Talking Gateway
- **Deployment**: Automated CI/CD to VPS server
- **Testing**: pytest with coverage reporting

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Africa's Talking account (for SMS functionality)
- Server with SSH access (for deployment)

### 1. Clone and Setup

```bash
git clone https://github.com/davidongora/Savannah.git
cd Savannah/savannah_test
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

The application uses raw SQL queries instead of Django models. Create the database schema:

```bash
# Connect to your PostgreSQL database
psql -h your_host -U your_user -d customer_order_db -f ../database/customer_order_db.sql
```

### 4. Environment Configuration

Set the required environment variables:

```bash
export POSTGRES_HOST=your_database_host
export POSTGRES_PORT=5432
export POSTGRES_DB=customer_order_db
export POSTGRES_USER=your_user
export POSTGRES_PASSWORD=your_password
export SECRET_KEY=your_secret_key_here
export AFRICAS_TALKING_API_KEY=your_api_key_here
export AFRICAS_TALKING_USERNAME=your_username_here
export AFRICAS_TALKING_SANDBOX=True
```

### 5. Run the Application

```bash
python manage.py runserver 0.0.0.0:8003
```

The API will be available at `http://localhost:8003`

### 6. Setup OIDC Authentication

Access the setup page to configure OpenID Connect:

```
http://localhost:8003/api/auth/setup-oidc/
```

This will create the necessary OAuth2 application for OIDC authentication.

## API Documentation

### Base URL

```
http://185.240.51.176:8003/api
```

### Authentication

The API uses **OpenID Connect (OIDC)** for authentication.

#### Getting an Access Token for API Testing

1. **Get a test token** (for development/testing):

```bash
# Get access token for API testing
curl -X POST http://185.240.51.176:8003/api/auth/test-token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

2. **Use the token** in API requests:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://185.240.51.176:8003/api/customers/
```

#### OIDC Authentication Flow

For production applications, use the standard OIDC flow:

1. **Authorization**: Direct users to `/o/authorize/` with appropriate parameters
2. **Token Exchange**: Exchange authorization code at `/o/token/`
3. **API Access**: Use the access token in Authorization header

---

## Authentication Endpoints

### OpenID Connect Discovery

**GET** `/o/.well-known/openid-configuration`

Discover OIDC configuration and endpoints.

**Response:**

```json
{
    "issuer": "http://localhost:8000/o",
    "authorization_endpoint": "http://localhost:8000/o/authorize/",
    "token_endpoint": "http://localhost:8000/o/token/",
    "userinfo_endpoint": "http://localhost:8000/o/userinfo/",
    "jwks_uri": "http://localhost:8000/o/.well-known/jwks.json",
    "scopes_supported": ["openid", "profile", "email"],
    "response_types_supported": ["code", "token", "id_token"],
    "subject_types_supported": ["public"],
    "id_token_signing_alg_values_supported": ["HS256"]
}
```

### OIDC Authorization

**GET** `/o/authorize/`

Initiate OpenID Connect authorization flow.

**Query Parameters:**

- `client_id` - Your application's client ID
- `response_type` - `code` for authorization code flow
- `scope` - Must include `openid` plus additional scopes (e.g., `openid profile email`)
- `redirect_uri` - Your application's callback URL
- `state` - Optional state parameter for security

### Token Exchange

**POST** `/o/token/`

Exchange authorization code for access and ID tokens.

**Request Body (Form Data):**

```
grant_type=authorization_code
code=<authorization_code>
client_id=<your_client_id>
client_secret=<your_client_secret>
redirect_uri=<your_redirect_uri>
```

**Response:**

```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "scope": "openid profile email"
}
```

### Get User Information

**GET** `/o/userinfo/`

Retrieve authenticated user information using OIDC.

**Headers:**

```http
Authorization: Bearer <access_token>
```

**Response:**

```json
{
    "sub": "user_identifier",
    "email": "user@example.com",
    "given_name": "John",
    "family_name": "Doe",
    "preferred_username": "johndoe"
}
```

### JWKS (JSON Web Key Set)

**GET** `/o/.well-known/jwks.json`

Retrieve public keys for token verification.

**Response:**

```json
{
    "keys": [
        {
            "kty": "RSA",
            "use": "sig",
            "kid": "key_id",
            "n": "public_key_modulus",
            "e": "AQAB"
        }
    ]
}
```

---

## Customer Endpoints

### List All Customers

**GET** `/api/customers/`

Retrieve all customers.

**Response:**

```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "code": "CUST001",
        "name": "John Doe",
        "phone_number": "+254712345678",
        "created_at": "2025-09-20T10:30:00Z",
        "updated_at": "2025-09-20T10:30:00Z"
    }
]
```

### Create Customer

**POST** `/api/customers/`

Create a new customer.

**Required Fields:**

- `code` (string): Unique customer code
- `name` (string): Customer full name
- `phone_number` (string): Phone number in international format

**Request Body:**

```json
{
    "code": "CUST001",
    "name": "John Doe",
    "phone_number": "+254712345678"
}
```

**Response (201 Created):**

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "CUST001",
    "name": "John Doe",
    "phone_number": "+254712345678",
    "created_at": "2025-09-20T10:30:00Z",
    "updated_at": "2025-09-20T10:30:00Z"
}
```

### Get Customer Details

**GET** `/api/customers/{customer_id}/`

Retrieve a specific customer by UUID.

**Path Parameters:**

- `customer_id` (UUID): Customer's unique identifier

**Response:**

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "CUST001",
    "name": "John Doe",
    "phone_number": "+254712345678",
    "created_at": "2025-09-20T10:30:00Z",
    "updated_at": "2025-09-20T10:30:00Z"
}
```

### Update Customer

**PUT** `/api/customers/{customer_id}/`

Update an existing customer.

**Request Body:**

```json
{
    "code": "CUST001_UPDATED",
    "name": "John Doe Updated",
    "phone_number": "+254712345679"
}
```

### Delete Customer

**DELETE** `/api/customers/{customer_id}/`

Delete a customer.

**Response:** `204 No Content`

---

## Order Endpoints

### List All Orders

**GET** `/api/orders/`

Retrieve all orders with customer information.

**Response:**

```json
[
    {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "item": "Laptop Computer",
        "amount": "1299.99",
        "order_time": "2025-09-20T11:00:00Z",
        "created_at": "2025-09-20T11:00:00Z",
        "customer_id": "550e8400-e29b-41d4-a716-446655440000",
        "customer_code": "CUST001",
        "customer_name": "John Doe",
        "customer_phone": "+254712345678"
    }
]
```

### Create Order

**POST** `/api/orders/`

Create a new order and send SMS notification to customer.

**Required Fields:**

- `customer_code` (string): Existing customer's code
- `item` (string): Order item description
- `amount` (number): Order amount/price

**Request Body:**

```json
{
    "customer_code": "CUST001",
    "item": "Laptop Computer",
    "amount": 1299.99
}
```

**Response (201 Created):**

```json
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "item": "Laptop Computer",
    "amount": "1299.99",
    "order_time": "2025-09-20T11:00:00Z",
    "created_at": "2025-09-20T11:00:00Z",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "customer_code": "CUST001",
    "customer_name": "John Doe",
    "customer_phone": "+254712345678",
    "sms_sent": true
}
```

### Get Order Details

**GET** `/api/orders/{order_id}/`

Retrieve a specific order by UUID.

**Path Parameters:**

- `order_id` (UUID): Order's unique identifier

### Update Order

**PUT** `/api/orders/{order_id}/`

Update an existing order.

**Request Body:**

```json
{
    "item": "Updated Item Name",
    "amount": 1499.99
}
```

### Delete Order

**DELETE** `/api/orders/{order_id}/`

Delete an order.

**Response:** `204 No Content`

### Get Orders by Customer (Query Parameter)

**GET** `/api/orders/by-customer/?customer_code=CUST001`

Retrieve all orders for a specific customer using query parameter.

**Query Parameters:**

- `customer_code` (string): Customer's code

### Get Orders by Customer (URL Parameter)

**GET** `/api/orders/customer/{customer_id}/`

Retrieve all orders for a specific customer using URL parameter.

**Path Parameters:**

- `customer_id` (UUID): Customer's unique identifier

---

## Error Responses

### 400 Bad Request

```json
{
    "error": "Missing required field: customer_code"
}
```

### 401 Unauthorized

```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found

```json
{
    "error": "Customer not found"
}
```

### 500 Internal Server Error

```json
{
    "error": "Failed to create order: Database connection error"
}
```

---

## Development Setup

### Local Development

1. **Create Virtual Environment:**

```bash
cd savannah_test
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

1. **Setup Database:**

```bash
# Create PostgreSQL database
createdb customer_order_db

# Run database schema (creates tables and sample data)
psql -d customer_order_db -f ../database/customer_order_db.sql
```

1. **Environment Variables:**

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=customer_order_db
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export SECRET_KEY=your-secret-key
export AFRICAS_TALKING_API_KEY=your-api-key
export AFRICAS_TALKING_USERNAME=your-username
export AFRICAS_TALKING_SANDBOX=True
```

1. **Run Development Server:**

```bash
python manage.py runserver
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest customers/tests.py -v
```

## Database Schema

### Customers Table

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);
```

### Orders Table

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    item VARCHAR(200) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## SMS Notification

When an order is created, the system automatically sends an SMS notification to the customer using Africa's Talking SMS gateway. The SMS contains:

- Customer name
- Order item
- Order amount
- Confirmation message

**Example SMS:**

```text
Hello John Doe! Your order for Laptop Computer worth KES 1299.99 has been received. Thank you!
```

## Deployment

### Automated CI/CD

The application uses GitHub Actions for automated testing and deployment:

1. **Testing**: Runs on every push and pull request
   - Sets up PostgreSQL test database
   - Installs dependencies
   - Runs unit tests with pytest

2. **Deployment**: Automatically deploys to VPS server on push to `main` branch
   - Copies files to server via SCP
   - Installs/updates dependencies
   - Restarts Django service
   - Verifies deployment

### GitHub Secrets Setup

For automated deployment, configure these secrets in your GitHub repository:

```text
SSH_PRIVATE_KEY  # Private SSH key for server access
SSH_HOST         # Server IP address (e.g., 185.240.51.176)
SSH_USER         # Server username (e.g., root)
```

### Manual Deployment

You can also deploy manually using the deployment script:

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The application is deployed at: `http://185.240.51.176:8003`

## License

This project is created for Savannah Informatics screening test.

## Support

## TODO

1. Create a simple Python or Go service
2. Design a simple customers and orders database (keep it simple)
3. Add a REST or GraphQL API to input / upload customers and orders:

- Customers have simple details e.g., name and code.
- Orders have simple details e.g., item, amount, and time.

4. Implement authentication and authorization via OpenID Connect
5. When an order is added, send the customer an SMS alerting them (you can use the
Africa’s Talking SMS gateway and sandbox)
6. Write unit tests (with coverage checking) and set up CI + automated CD. You can deploy
to any PAAS/FAAS/IAAS of your choice
7. Write a README for the project and host it on your GitHub
