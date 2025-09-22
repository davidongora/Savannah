# Savannah Customer Orders API

Django REST API for customers and orders with SMS notifications. PostgreSQL + OIDC authentication.

## Features
 Customer/Order CRUD   OIDC Auth   SMS Integration   CI/CD   Tests

## Setup

`ash
git clone https://github.com/davidongora/Savannah.git
cd Savannah/savannah_test
pip install -r requirements.txt

# Database
psql -h host -U user -d customer_order_db -f ../database/customer_order_db.sql

# Environment
export POSTGRES_HOST=your_host
export POSTGRES_DB=customer_order_db
export POSTGRES_USER=your_user
export POSTGRES_PASSWORD=your_password
export SECRET_KEY=your_secret
export MOBILE_SASA_API_TOKEN=jiTISsK2kmrtpEpL724i0x0TJiGnZt1yfTSBozWoMTDul7GkwldCS7SbCjPR

# Run
python manage.py runserver 0.0.0.0:8003
curl -X POST http://localhost:8003/api/auth/setup-oidc/
`

## Testing

`ash
# 1. Create account
curl -X POST http://185.240.51.176:8003/api/auth/create-user/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@test.com", "password": "pass123!"}'

# 2. Get token
curl -X POST http://185.240.51.176:8003/api/auth/test-token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "pass123!"}'

# 3. Create customer
curl -X POST http://185.240.51.176:8003/api/customers/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "code": "CUST001", "phone": "+254712345678"}'

# 4. Create order (sends SMS)
curl -X POST http://185.240.51.176:8003/api/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "item": "Product", "amount": 99.99}'
`

## Endpoints

**Auth:** /api/auth/create-user/  /api/auth/test-token/  /api/auth/users/

**Customers:** GET|POST /api/customers/  GET|PUT|DELETE /api/customers/{id}/
`json
{"name": "Name", "code": "CODE", "phone": "+254712345678"}
`

**Orders:** GET|POST /api/orders/  GET|PUT|DELETE /api/orders/{id}/
`json
{"customer_id": 1, "item": "Product", "amount": 99.99}
`

**OIDC:** /o/.well-known/openid-configuration  /o/authorize/  /o/token/  /o/userinfo/

## Quick Commands

`ash
# Check users
curl http://185.240.51.176:8003/api/auth/users/

# Run tests
python -m pytest --cov=.

# Browser access
http://185.240.51.176:8003/api/auth/register/
http://185.240.51.176:8003/oidc/authenticate/
`

## Live Deployment
- **API:** http://185.240.51.176:8003
- **GitHub:** https://github.com/davidongora/Savannah
- **Stack:** Django 4.2.7  PostgreSQL  OIDC  Mobile Sasa SMS  GitHub Actions
