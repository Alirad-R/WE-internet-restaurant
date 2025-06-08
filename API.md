# API Documentation

## Authentication

### Obtain JWT Token
```http
POST /api/auth/token/
```
Request body:
```json
{
    "username": "string",
    "password": "string"
}
```
Response:
```json
{
    "access": "string",
    "refresh": "string"
}
```

### Refresh Token
```http
POST /api/auth/token/refresh/
```
Request body:
```json
{
    "refresh": "string"
}
```
Response:
```json
{
    "access": "string"
}
```

## Products

### List Products
```http
GET /api/products/
```
Query Parameters:
- `category`: Filter by category ID
- `search`: Search in name and description
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `ordering`: Sort by field (e.g., -price, name)

Response:
```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {
            "id": 0,
            "name": "string",
            "description": "string",
            "price": "0.00",
            "category": {
                "id": 0,
                "name": "string"
            },
            "image": "string",
            "is_available": true
        }
    ]
}
```

### Create Product
```http
POST /api/products/
```
Request body:
```json
{
    "name": "string",
    "description": "string",
    "price": "0.00",
    "category_id": 0,
    "image": "file",
    "is_available": true
}
```

## Orders

### Create Order
```http
POST /api/orders/
```
Request body:
```json
{
    "items": [
        {
            "product_id": 0,
            "quantity": 0
        }
    ],
    "delivery_address": "string",
    "special_instructions": "string",
    "coupon_code": "string"
}
```
Response:
```json
{
    "id": 0,
    "order_number": "string",
    "status": "pending",
    "items": [...],
    "subtotal": "0.00",
    "discount": "0.00",
    "total": "0.00",
    "created_at": "datetime"
}
```

### List Orders
```http
GET /api/orders/
```
Query Parameters:
- `status`: Filter by order status
- `from_date`: Filter from date
- `to_date`: Filter to date

Response:
```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {
            "id": 0,
            "order_number": "string",
            "status": "string",
            "total": "0.00",
            "created_at": "datetime"
        }
    ]
}
```

## Coupons

### Create Coupon
```http
POST /api/coupons/
```
Request body:
```json
{
    "code": "string",
    "description": "string",
    "discount_type": "percentage",
    "discount_value": "0.00",
    "valid_from": "datetime",
    "valid_until": "datetime",
    "max_uses": 0,
    "customer_tier": "all",
    "min_order_value": "0.00",
    "applicable_products": [0],
    "applicable_categories": [0]
}
```

### Validate Coupon
```http
POST /api/coupons/{id}/validate/
```
Request body:
```json
{
    "cart_value": "0.00",
    "cart_items": [
        {
            "product_id": 0,
            "quantity": 0
        }
    ]
}
```
Response:
```json
{
    "is_valid": true,
    "message": "string",
    "discount_amount": "0.00"
}
```

### Apply Coupon
```http
POST /api/coupons/{id}/apply/
```
Request body:
```json
{
    "order_id": 0
}
```
Response:
```json
{
    "success": true,
    "discount_amount": "0.00",
    "new_total": "0.00"
}
```

## Notifications

### List Notifications
```http
GET /api/notifications/
```
Query Parameters:
- `read`: Filter by read status (true/false)
- `type`: Filter by notification type

Response:
```json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
        {
            "id": 0,
            "type": "string",
            "message": "string",
            "created_at": "datetime",
            "read_at": "datetime"
        }
    ]
}
```

### Mark Notification as Read
```http
PUT /api/notifications/{id}/read/
```
Response:
```json
{
    "id": 0,
    "read_at": "datetime"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "string",
    "detail": "string"
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

## Rate Limiting

The API implements rate limiting:
- Anonymous users: 100 requests per day
- Authenticated users: 1000 requests per day

Rate limit response (429 Too Many Requests):
```json
{
    "detail": "Request was throttled. Expected available in X seconds."
}
``` 