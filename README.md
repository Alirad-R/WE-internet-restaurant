# Restaurant Backend Management System

A comprehensive Django-based restaurant backend system with advanced features including user management, product catalog, order processing, coupon system, real-time notifications, and automated stock monitoring.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Mobile App     │    │   API Clients   │
│   Application   │    │                  │    │                 │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      Django REST        │
                    │      Framework API      │
                    │                         │
                    │  ┌─────────────────┐   │
                    │  │ JWT Auth        │   │
                    │  │ Middleware      │   │
                    │  └─────────────────┘   │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Business Logic │    │ Background Tasks │    │    Database      │
│                │    │                  │    │                  │
│ • Accounts     │    │ • Celery Workers │    │ • MySQL          │
│ • Products     │    │ • Celery Beat    │    │ • User Data      │
│ • Orders       │    │ • Redis Broker   │    │ • Orders         │
│ • Coupons      │    │                  │    │ • Products       │
│ • Alerts       │    │                  │    │ • Transactions   │
└────────────────┘    └──────────────────┘    └──────────────────┘
```

## ✨ Key Features

### 🔐 User Management
- **JWT-based Authentication** with access and refresh tokens
- **Custom User Model** with profiles and preferences
- **Customer Profiles** with delivery addresses and dietary restrictions
- **Password Reset** functionality via email
- **Admin User Management** with role-based access

### 🛍️ Product Catalog
- **Categories and Products** with images and descriptions
- **Product Attributes** and tagging system
- **Stock Management** with real-time monitoring
- **Search and Filtering** capabilities
- **Featured Products** highlighting

### 🛒 Shopping Cart & Orders
- **Persistent Shopping Cart** per user
- **Order Processing** with multiple status tracking
- **Payment Integration** via built-in wallet system
- **Order Status Workflow**: Pending → Processing → Preparing → Ready → Shipped → Delivered
- **Delivery Methods**: Pickup and Delivery options
- **Order History** and tracking

### 🎫 Advanced Coupon System
- **Multiple Discount Types**:
  - Percentage discounts (e.g., 20% off)
  - Fixed amount discounts (e.g., $5 off)
  - Buy X Get Y offers
  - Tiered discounts (spend more, save more)
- **Customer Tier Support**: ALL, NEW (0 orders), REGULAR (3+ orders, $100+ spent), VIP (10+ orders, $1000+ spent)
- **Smart Validation**: Minimum order value, usage limits, expiry dates
- **Automated Management**: Daily expiry checks, usage tracking
- **Referral System** for customer acquisition

### 💰 Wallet & Payment System
- **Digital Wallet** for each user
- **Transaction History** with detailed records
- **Balance Management** for order payments
- **Transaction Types**: Deposits, purchases, refunds

### 🚨 Alert & Notification System
- **Real-time Stock Monitoring** with configurable thresholds
- **Automated Alerts** for low stock (Warning/Critical levels)
- **Staff Notifications** via email and in-app alerts
- **Coupon Notifications** for expiring offers
- **System Notifications** for important events

### 📱 Background Processing
- **Celery Workers** for async task processing
- **Scheduled Tasks**:
  - Daily coupon expiry checks
  - Twice-daily cleanup of expired coupons
  - Stock level monitoring
  - Email notification sending

## 🛠️ Technology Stack

- **Backend Framework**: Django 5.2 + Django REST Framework
- **Database**: MySQL (cafe_db)
- **Authentication**: JWT (Simple JWT)
- **Task Queue**: Celery with Redis broker
- **Caching**: Redis
- **Email**: SMTP/Console backend
- **File Storage**: Local (development) / AWS S3 (production)
- **API Documentation**: Auto-generated via DRF

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd backend_project
```

### 2. Create Virtual Environment
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE cafe_db;
CREATE USER 'cafedev'@'localhost' IDENTIFIED BY 'Aali1384';
GRANT ALL PRIVILEGES ON cafe_db.* TO 'cafedev'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Environment Configuration
Create `.env` file in root directory:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DATABASE_URL=mysql://cafedev:Aali1384@localhost:3306/cafe_db
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourrestaurant.com
```

### 6. Database Migration
```bash
python manage.py migrate
```

### 7. Create Sample Data (Optional)
```bash
python create_sample_data.py
```

### 8. Create Superuser
```bash
python manage.py createsuperuser
```

### 9. Start Development Server
```bash
python manage.py runserver
```

### 10. Start Background Workers (New Terminal)
```bash
# Start Celery worker
celery -A backend_project worker -l info

# Start Celery beat scheduler (New Terminal)
celery -A backend_project beat -l info
```

## 📁 Project Structure

```
backend_project/
├── accounts/              # User management & authentication
│   ├── models.py         # User, CustomerProfile, OTP models
│   ├── views.py          # Auth views, user management
│   ├── serializers.py    # User serialization
│   ├── middleware.py     # JWT authentication middleware
│   └── urls.py           # Auth endpoints
├── products/             # Product catalog management
│   ├── models.py         # Category, Product, Attribute models
│   ├── views.py          # Product CRUD operations
│   └── urls.py           # Product endpoints
├── orders/               # Order processing & cart management
│   ├── models.py         # Order, OrderItem, Cart, Wallet models
│   ├── views.py          # Order processing, cart operations
│   ├── reports.py        # Order analytics and reporting
│   └── urls.py           # Order endpoints
├── coupons/              # Coupon system
│   ├── models.py         # Coupon, CouponUsage, Notification models
│   ├── views.py          # Coupon CRUD and validation
│   ├── tasks.py          # Background coupon tasks
│   └── urls.py           # Coupon endpoints
├── alerts/               # Alert & notification system
│   ├── models.py         # ProductAlert, AlertNotification models
│   ├── services.py       # Alert processing logic
│   ├── views.py          # Alert management views
│   └── urls.py           # Alert endpoints
├── backend_project/      # Core Django configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL routing
│   ├── celery.py         # Celery configuration
│   └── wsgi.py           # WSGI application
├── media/                # User uploaded files
├── staticfiles/          # Static files for production
├── requirements.txt      # Python dependencies
└── manage.py             # Django management script
```

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/login/                    # User login
POST   /api/auth/users/                    # User registration
GET    /api/auth/users/                    # List users (admin)
PUT    /api/auth/users/{id}/               # Update user
DELETE /api/auth/users/{id}/               # Delete user
GET    /api/auth/profile/                  # Get user profile
PUT    /api/auth/profile/                  # Update user profile
POST   /api/auth/password-reset/request/   # Request password reset
POST   /api/auth/password-reset/confirm/   # Confirm password reset
GET    /api/auth/profiles/                 # List customer profiles
```

### Products
```
GET    /api/products/                      # List products
POST   /api/products/                      # Create product (admin)
GET    /api/products/{id}/                 # Get product details
PUT    /api/products/{id}/                 # Update product (admin)
DELETE /api/products/{id}/                 # Delete product (admin)
GET    /api/products/categories/           # List categories
POST   /api/products/categories/           # Create category (admin)
GET    /api/products/featured/             # Get featured products
```

### Cart & Orders
```
GET    /api/orders/cart/                   # Get user cart
POST   /api/orders/cart/add_item/          # Add item to cart
PUT    /api/orders/cart/update_item/{id}/  # Update cart item
DELETE /api/orders/cart/remove_item/{id}/  # Remove cart item
POST   /api/orders/cart/checkout/          # Create order from cart
GET    /api/orders/                        # List user orders
GET    /api/orders/{id}/                   # Get order details
PUT    /api/orders/{id}/                   # Update order status (admin)
POST   /api/orders/{id}/pay/               # Pay for order
GET    /api/orders/wallet/                 # Get wallet balance
POST   /api/orders/wallet/deposit/         # Add funds to wallet
```

### Coupons
```
GET    /api/coupons/                       # List available coupons
POST   /api/coupons/                       # Create coupon (admin)
GET    /api/coupons/{id}/                  # Get coupon details
PUT    /api/coupons/{id}/                  # Update coupon (admin)
DELETE /api/coupons/{id}/                  # Delete coupon (admin)
POST   /api/coupons/validate/              # Validate coupon code
POST   /api/coupons/{id}/apply/            # Apply coupon to order
GET    /api/coupons/my-coupons/            # Get user's available coupons
GET    /api/coupons/usage-history/         # Get user's coupon usage
```

### Alerts & Notifications
```
GET    /api/alerts/                        # List alerts (staff)
POST   /api/alerts/                        # Create alert (admin)
PUT    /api/alerts/{id}/resolve/           # Resolve alert (staff)
GET    /api/alerts/notifications/          # Get user notifications
POST   /api/alerts/notifications/mark-all-read/  # Mark all as read
POST   /api/alerts/notifications/{id}/mark-read/ # Mark notification as read
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test orders
python manage.py test coupons
python manage.py test alerts

# Run with coverage
pip install coverage
coverage run manage.py test
coverage report
coverage html
```

### Test Coverage
The project includes comprehensive tests for:
- Authentication flows
- Order processing
- Coupon validation
- Alert generation
- API endpoints

## 🚀 Production Deployment

### Environment Variables
```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-production-secret-key
DATABASE_URL=mysql://user:pass@host:port/dbname
CELERY_BROKER_URL=redis://redis-host:6379/1
CELERY_RESULT_BACKEND=redis://redis-host:6379/2
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
EMAIL_HOST=your-smtp-host
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Security Settings (Production)
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS with SSL certificates
- Set up proper CORS origins
- Configure secure cookie settings
- Use environment variables for secrets

### Server Requirements
- **Web Server**: Nginx + Gunicorn
- **Database**: MySQL 8.0+ or PostgreSQL 12+
- **Cache**: Redis 6.0+
- **Task Queue**: Celery workers
- **Storage**: AWS S3 for media files
- **Email**: SMTP service (SendGrid, SES, etc.)

## 📊 Monitoring & Analytics

### Celery Monitoring
```bash
# Monitor Celery workers
celery -A backend_project inspect active
celery -A backend_project inspect stats

# Monitor Celery beat
celery -A backend_project beat --detach
```

### Database Monitoring
- Track order volume and revenue
- Monitor coupon usage rates
- Alert response times
- Customer behavior analytics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages
- Add type hints where applicable

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints
- Test with the provided sample data

---

**Happy Coding! 🍽️**
