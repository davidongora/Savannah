# Environment Setup

## Environment Variables

This project uses environment variables to manage sensitive configuration data. 

### Setup Instructions

1. **Copy the example environment file:**
   ```bash
   cd Docker
   cp .env.example .env
   ```

2. **Edit the `.env` file with your actual values:**
   ```bash
   # Update these values with your actual credentials
   POSTGRES_PASSWORD=your_actual_secure_password
   SECRET_KEY=your_actual_django_secret_key
   AFRICAS_TALKING_API_KEY=your_actual_api_key
   AFRICAS_TALKING_USERNAME=your_actual_username
   ```

### Required Environment Variables

| Variable | Description | Default/Example |
|----------|-------------|-----------------|
| `POSTGRES_DB` | PostgreSQL database name | `customer_order_db` |
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `change_this_password` |
| `POSTGRES_HOST` | PostgreSQL host (for Django) | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_HOST_AUTH_METHOD` | Auth method | `trust` |
| `DEBUG` | Django debug mode | `False` |
| `SECRET_KEY` | Django secret key | Generate new one |
| `AFRICAS_TALKING_API_KEY` | Africa's Talking API key | Your API key |
| `AFRICAS_TALKING_USERNAME` | Africa's Talking username | Your username |
| `AFRICAS_TALKING_SANDBOX` | Use sandbox mode | `True` |

### Security Notes

- ⚠️ **Never commit `.env` files to version control**
- ✅ Use strong, unique passwords
- ✅ Generate a new Django SECRET_KEY for production
- ✅ Keep API keys secure and rotate them regularly

### Running the Application

After setting up your `.env` file:

```bash
cd Docker
docker-compose up -d
```