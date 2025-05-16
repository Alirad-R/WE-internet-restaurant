# WE-internet-restaurant
Online restaurant for businesses

## Project Structure

The restaurant project follows a clean, modular Django architecture:

### Core Apps

1. **accounts**
   - User authentication and management
   - Customer profile management
   - Features:
     - JWT authentication with access and refresh tokens
     - Password reset with OTP verification
     - Custom user model with extended fields
     - Customer profiles with dietary preferences
     - Full CRUD operations through REST API

2. **products**
   - Product catalog management
   - Product categories
   - Menu items

3. **orders**
   - Shopping cart management
   - Order processing and tracking
   - Order history and details
   - Features:
     - Persistent shopping cart for users
     - Order creation from cart
     - Order status tracking
     - Order cancellation

### API Endpoints

#### Authentication and User Management
- `POST /api/auth/login/` - User authentication
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/auth/password-reset/request/` - Request password reset
- `POST /api/auth/password-reset/confirm/` - Confirm password reset with OTP
- `GET /api/auth/profile/` - Get user profile with customer data
- `PUT /api/auth/profile/` - Update user profile and customer data

#### User CRUD
- `GET|POST /api/auth/users/` - List or create users
- `GET|PUT|DELETE /api/auth/users/{id}/` - Retrieve, update, or delete a user
- `GET /api/auth/users/{id}/retrieve_with_profile/` - Get user with profile information

#### Customer Profile Management
- `GET|POST /api/auth/customer-profiles/` - List or create customer profiles
- `GET|PUT|PATCH|DELETE /api/auth/customer-profiles/{id}/` - Manage customer profile
- `GET /api/auth/customer-profiles/me/` - Get current user's customer profile

#### Product Management
- `GET|POST /api/products/products/` - List or create products
- `GET|PUT|PATCH|DELETE /api/products/products/{id}/` - Manage products
- `GET /api/products/products/featured/` - Get featured products

#### Category Management
- `GET|POST /api/products/categories/` - List or create categories
- `GET|PUT|PATCH|DELETE /api/products/categories/{id}/` - Manage categories

#### Cart Management
- `GET /api/orders/cart/` - View current cart
- `POST /api/orders/cart/add_item/` - Add item to cart
- `POST /api/orders/cart/remove_item/` - Remove item from cart
- `POST /api/orders/cart/update_quantity/` - Update item quantity in cart
- `POST /api/orders/cart/clear/` - Clear all items from cart
- `POST /api/orders/cart/checkout/` - Create order from cart items

#### Order Management
- `GET|POST /api/orders/orders/` - List or create orders
- `GET|PUT|PATCH|DELETE /api/orders/orders/{id}/` - Manage orders
- `POST /api/orders/orders/{id}/cancel/` - Cancel a pending order

### Project Directory Structure

```
restaurant_project/
│
├── accounts/                # Auth and user/profile management
│   ├── migrations/
│   ├── admin.py            # Admin interface for User and CustomerProfile
│   ├── apps.py
│   ├── models.py           # User, CustomerProfile, and OTP models
│   ├── serializers.py      # User and CustomerProfile serializers
│   ├── urls.py             # Auth and profile endpoints
│   └── views.py            # Auth and profile views
│
├── backend_project/         # Main project configuration
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── products/                # Product catalog
│   ├── migrations/
│   ├── admin.py            # Admin interface for Product and Category
│   ├── apps.py
│   ├── models.py           # Product and Category models
│   ├── serializers.py      # Product and Category serializers
│   ├── urls.py             # Product and Category endpoints
│   └── views.py            # Product and Category views
│
├── orders/                # Order and cart management
│   ├── migrations/
│   ├── admin.py           # Admin interface for Order and Cart
│   ├── apps.py
│   ├── models.py          # Order, OrderItem, Cart, and CartItem models
│   ├── serializers.py     # Order and Cart serializers
│   ├── urls.py            # Order and Cart endpoints
│   └── views.py           # Order and Cart views
│
├── manage.py                # Django management script
└── README.md                # Project documentation
```

### Customer Profile Implementation

The customer profile management feature includes:

- `CustomerProfile` model in the `accounts` app that extends the User model via OneToOneField
- Fields include: phone_number, address, city, state, country, postal_code, preferences, allergies, dietary_restrictions
- Auto-creation of profile when a new user is registered
- Full CRUD operations through REST API
- JSON field for storing flexible preference data
- Admin interface for easy management

### Cart and Order Implementation

The cart and order management system includes:

- Shopping cart that persists between user sessions
- Cart items with product references and quantities
- Order creation from cart items
- Order tracking with status updates
- Support for multiple order items per order
- Transaction support to ensure data integrity
- Admin interface for order management
