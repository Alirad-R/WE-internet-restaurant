# Restaurant Management System

A comprehensive Django-based restaurant management system with advanced features including order management, coupon system, and notifications.

## Features

### Core Features
- User Authentication & Authorization
- Product Management
- Order Processing
- Advanced Coupon System
- Real-time Notifications
- Admin Dashboard

### Coupon System
- Multiple discount types:
  - Percentage discounts
  - Fixed amount discounts
  - Buy X Get Y offers
  - Tiered discounts
- Customer tier-based rules (ALL, NEW, REGULAR, VIP)
- Time and seasonal restrictions
- Usage tracking and validation
- Referral system
- Integration with orders

### Technical Features
- JWT Authentication
- Celery for async tasks
- Redis caching
- S3/Local file storage
- Email notifications
- Background task processing

## Technology Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Caching**: Redis
- **Task Queue**: Celery
- **Storage**: AWS S3 (Production), Local (Development)
- **Authentication**: JWT (JSON Web Tokens)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Alirad-R/WE-internet-restaurant.git
cd WE-internet-restaurant
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```env
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DATABASE_URL=your_database_url
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_STORAGE_BUCKET_NAME=your_bucket_name
EMAIL_HOST=your_email_host
EMAIL_PORT=587
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Project Structure

```
restaurant_project/
├── accounts/          # User management
├── products/          # Product management
├── orders/           # Order processing
├── coupons/          # Coupon system
├── alerts/           # Notification system
├── backend_project/  # Core configuration
└── manage.py
```

## API Documentation

### Authentication
- POST `/api/auth/token/` - Obtain JWT token
- POST `/api/auth/token/refresh/` - Refresh JWT token

### Products
- GET `/api/products/` - List products
- POST `/api/products/` - Create product
- GET `/api/products/{id}/` - Retrieve product
- PUT `/api/products/{id}/` - Update product
- DELETE `/api/products/{id}/` - Delete product

### Orders
- GET `/api/orders/` - List orders
- POST `/api/orders/` - Create order
- GET `/api/orders/{id}/` - Retrieve order
- PUT `/api/orders/{id}/` - Update order
- DELETE `/api/orders/{id}/` - Delete order

### Coupons
- GET `/api/coupons/` - List coupons
- POST `/api/coupons/` - Create coupon
- GET `/api/coupons/{id}/` - Retrieve coupon
- PUT `/api/coupons/{id}/` - Update coupon
- DELETE `/api/coupons/{id}/` - Delete coupon
- POST `/api/coupons/{id}/validate/` - Validate coupon
- POST `/api/coupons/{id}/apply/` - Apply coupon

### Notifications
- GET `/api/notifications/` - List notifications
- PUT `/api/notifications/{id}/read/` - Mark notification as read

## Development

### Running Tests
```bash
python manage.py test
```

### Running Celery
```bash
celery -A backend_project worker -l info
celery -A backend_project beat -l info
```

### Code Style
The project follows PEP 8 style guide. Run linting:
```bash
flake8
```

## Deployment

### Production Setup
1. Set DEBUG=False in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up proper email backend
4. Configure AWS S3 for file storage
5. Set up proper CORS settings
6. Configure proper cache backend
7. Set up proper logging

### Server Requirements
- Python 3.8+
- PostgreSQL
- Redis
- Celery
- Nginx (recommended)
- Gunicorn (recommended)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
