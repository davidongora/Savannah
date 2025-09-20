# Savannah Customer Orders API

A Django REST API service for managing customers and orders with SMS notifications. Built with PostgreSQL database and Africa's Talking SMS gateway integration.

## Features

- 🏪 Customer management (CRUD operations)
- 📦 Order management with customer relationships
- 🔐 OpenID Connect (OIDC) authentication
- 📱 SMS notifications via Africa's Talking
- 🗄️ PostgreSQL database with raw SQL queries
- 🐳 Docker containerization
- ✅ Comprehensive unit tests with coverage
- 🌐 RESTful API design

## Tech Stack

- **Backend**: Django 5.2.6 + Django REST Framework
- **Database**: PostgreSQL 14 with UUID primary keys
- **Authentication**: OpenID Connect (OIDC)
- **SMS Service**: Africa's Talking Gateway
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with coverage reporting

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- Africa's Talking account (for SMS functionality)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd savannah
```

### 2. Environment Configuration

Copy the environment example file:

```bash
cp Docker/.env.example Docker/.env
```

Edit `Docker/.env` with your configuration:

```dotenv
# Database Configuration
POSTGRES_DB=customer_order_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django Configuration
DEBUG=False
SECRET_KEY=your_secret_key_here

# Africa's Talking SMS Configuration
AFRICAS_TALKING_API_KEY=your_api_key_here
AFRICAS_TALKING_USERNAME=your_username_here
AFRICAS_TALKING_SANDBOX=True
```

### 3. Run with Docker

```bash
cd Docker
docker-compose up -d
```

The API will be available at `http://localhost:8000`

### 4. Setup OAuth2 Application for OIDC

Create an OAuth2 application for OpenID Connect authentication:

```bash
# Create superuser first (if not already created)
docker-compose exec web python manage.py createsuperuser

# Setup OAuth2 application
docker-compose exec web python manage.py setup_oauth
```

This command will create an OAuth2 application and display the client credentials:

```text
OAuth2 Application created successfully!
Client ID: BlCsN7kGpNohIxA9P4UiPeVcY0P5Nt5aWvWcUq0O
Client Secret: [Generated Secret]
Authorization Grant Type: authorization-code
Client Type: confidential
```

**Important**: Save these credentials securely - you'll need them for OIDC authentication.

### 5. OIDC Environment Variables

Add these OIDC configuration variables to your `Docker/.env` file:

```dotenv
# OpenID Connect Configuration
OIDC_RP_CLIENT_ID=BlCsN7kGpNohIxA9P4UiPeVcY0P5Nt5aWvWcUq0O
OIDC_RP_CLIENT_SECRET=your_generated_client_secret
OIDC_OP_AUTHORIZATION_ENDPOINT=http://localhost:8000/o/authorize/
OIDC_OP_TOKEN_ENDPOINT=http://localhost:8000/o/token/
OIDC_OP_USER_ENDPOINT=http://localhost:8000/o/userinfo/
OIDC_OP_JWKS_ENDPOINT=http://localhost:8000/o/.well-known/jwks.json
OIDC_RP_SCOPES=openid profile email
OIDC_RP_SIGN_ALGO=HS256
```

### 6. Create Superuser (Optional)

```bash
docker-compose exec web python manage.py createsuperuser
```

## API Documentation

### Base URL

```
http://localhost:8000/api
```

### Authentication

The API uses **OpenID Connect (OIDC)** for authentication, which is built on OAuth2.

All endpoints (except authentication and discovery) require valid OIDC authentication credentials.

For OIDC authentication, include the Bearer token in the Authorization header:

```http
Authorization: Bearer <your_oidc_access_token>
```

**Note**: While the underlying infrastructure uses OAuth2 for OIDC implementation, the API is designed to be consumed using standard OpenID Connect flows.

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
python -m venv myvenv
source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate
```

2. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

3. **Setup Database:**

```bash
# Start PostgreSQL with Docker
docker run -d \
  --name savannah-postgres \
  -e POSTGRES_DB=customer_order_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:14

# Run database schema
psql -h localhost -U postgres -d customer_order_db -f ../database/customer_order_db.sql
```

4. **Environment Variables:**

```bash
export DJANGO_SETTINGS_MODULE=savannah_test.settings
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

5. **Run Development Server:**

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
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Orders Table

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    item VARCHAR(200) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    order_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## SMS Notification

When an order is created, the system automatically sends an SMS notification to the customer using Africa's Talking SMS gateway. The SMS contains:

- Customer name
- Order item
- Order amount
- Confirmation message

**Example SMS:**

```
Hello John Doe! Your order for Laptop Computer worth KES 1299.99 has been received. Thank you!
```

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
