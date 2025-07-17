# API Endpoint Examples

---

## Authentication

### Obtain JWT Token
**POST** `/api/auth/token/`
```json
// Request
{
  "username": "user",
  "password": "pass"
}
// Response
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}
```

### Refresh Token
**POST** `/api/auth/token/refresh/`
```json
// Request
{
  "refresh": "jwt_refresh_token"
}
// Response
{
  "access": "new_jwt_access_token"
}
```

---

## User Registration & Profile

### Register User
**POST** `/api/auth/users/`
```json
// Request
{
  "username": "newuser",
  "password": "yourpassword",
  "email": "user@example.com"
}
// Response
{
  "id": 5,
  "username": "newuser",
  "email": "user@example.com"
}
```

### Get Current User Profile
**GET** `/api/auth/profiles/me/`
```json
// Response
{
  "id": 5,
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "",
  "last_name": ""
}
```

---

## Products

### List Products
**GET** `/api/products/?search=burger&ordering=-price`
```json
// Response
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Burger",
      "description": "Tasty beef burger",
      "price": "5.99",
      "category": { "id": 2, "name": "Fast Food" },
      "image": "/media/products/burger.jpg",
      "is_available": true
    }
  ]
}
```

### Create Product
**POST** `/api/products/`
```json
// Request
{
  "name": "Burger",
  "description": "Tasty beef burger",
  "price": "5.99",
  "category_id": 2,
  "is_available": true
}
// Response
{
  "id": 1,
  "name": "Burger",
  "description": "Tasty beef burger",
  "price": "5.99",
  "category": { "id": 2, "name": "Fast Food" },
  "image": null,
  "is_available": true
}
```

---

## Orders

### Create Order
**POST** `/api/orders/orders/`
```json
// Request
{
  "items": [
    { "product_id": 1, "quantity": 2 }
  ],
  "delivery_address": "123 Main St",
  "special_instructions": "Leave at the door",
  "coupon_code": "SAVE10"
}
// Response
{
  "id": 10,
  "order_number": "ORD-20230701-0001",
  "status": "pending",
  "items": [
    { "product_id": 1, "quantity": 2, "name": "Burger", "unit_price": "5.99" }
  ],
  "subtotal": "11.98",
  "discount": "1.20",
  "total": "10.78",
  "created_at": "2025-07-17T16:00:00Z"
}
```

### List Orders
**GET** `/api/orders/orders/`
```json
// Response
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "order_number": "ORD-20230701-0001",
      "status": "pending",
      "total": "10.78",
      "created_at": "2025-07-17T16:00:00Z"
    }
  ]
}
```

---

## Coupons

### Create Coupon
**POST** `/api/coupons/coupons/`
```json
// Request
{
  "code": "SAVE10",
  "description": "10% off",
  "discount_type": "percentage",
  "discount_value": "10.00",
  "valid_from": "2025-07-01T00:00:00Z",
  "valid_until": "2025-08-01T00:00:00Z",
  "max_uses": 100,
  "customer_tier": "all",
  "min_order_value": "20.00",
  "applicable_products": [1],
  "applicable_categories": [2]
}
// Response
{
  "id": 3,
  "code": "SAVE10",
  "description": "10% off",
  "discount_type": "percentage",
  "discount_value": "10.00",
  "valid_from": "2025-07-01T00:00:00Z",
  "valid_until": "2025-08-01T00:00:00Z",
  "max_uses": 100,
  "customer_tier": "all",
  "min_order_value": "20.00",
  "applicable_products": [1],
  "applicable_categories": [2]
}
```

### Validate Coupon
**POST** `/api/coupons/coupons/3/validate/`
```json
// Request
{
  "cart_value": "25.00",
  "cart_items": [
    { "product_id": 1, "quantity": 2 }
  ]
}
// Response
{
  "is_valid": true,
  "message": "Coupon applied successfully.",
  "discount_amount": "2.50"
}
```

---

## Alerts & Notifications

### Create Product Alert
**POST** `/api/alerts/alerts/`
```json
// Request
{
  "product_id": 1,
  "alert_type": "low_stock"
}
// Response
{
  "id": 5,
  "product_id": 1,
  "alert_type": "low_stock",
  "is_active": true,
  "created_at": "2025-07-17T16:00:00Z"
}
``` 