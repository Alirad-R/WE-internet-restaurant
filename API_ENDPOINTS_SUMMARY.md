# API Endpoints Summary

---

## Authentication (accounts)

| Method | Endpoint                                 | Description                        |
|--------|------------------------------------------|------------------------------------|
| POST   | `/api/auth/token/`                       | Obtain JWT token                   | Needs fix
| POST   | `/api/auth/token/refresh/`               | Refresh JWT token                  | Needs fix
| POST   | `/api/auth/login/`                       | Login (custom view)                | Works fine
| POST   | `/api/auth/password-reset/request/`      | Request password reset             |
| POST   | `/api/auth/password-reset/confirm/`      | Confirm password reset             |
| GET    | `/api/auth/profile/`                     | Get current user's profile         | Works fine

**Usage Examples:**
```bash
# Obtain JWT token
curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"user","password":"pass"}' \
     http://localhost:8000/api/auth/token/

# Refresh token
curl -X POST -H "Content-Type: application/json" \
     -d '{"refresh":"<refresh_token>"}' \
     http://localhost:8000/api/auth/token/refresh/
```

---

## Users & Profiles

| Method    | Endpoint                              | Description                        |
|-----------|---------------------------------------|------------------------------------|
| GET/POST  | `/api/auth/users/`                    | List or create users               | Works fine (You need to put the admin token for auth)
| GET/PUT/DELETE | `/api/auth/users/{id}/`           | Retrieve, update, or delete user   | Works fine
| GET/PUT   | `/api/auth/profiles/`                 | List or update customer profile    | Works fine
| GET       | `/api/auth/profiles/me/`              | Get current user's profile         | Works fine
| GET/POST  | `/api/auth/admin/users/`              | Admin user management              | Works fine

**Example:**
```http
POST /api/auth/users/
{
  "username": "newuser",
  "password": "..."
}
```

---

## Products

| Method    | Endpoint                              | Description                        |
|-----------|---------------------------------------|------------------------------------|
| GET/POST  | `/api/products/`                      | List or create products            | 
| GET/PUT/DELETE | `/api/products/{id}/`             | Retrieve, update, or delete product|
| GET       | `/api/products/featured/`             | List featured products             |
| GET/POST  | `/api/products/categories/`           | List or create categories          |
| GET/POST  | `/api/products/attributes/`           | List or create attributes          |
| GET/POST  | `/api/products/attribute_values/`     | List or create attribute values    |
| GET/POST  | `/api/products/tags/`                 | List or create tags                |
| GET/POST  | `/api/products/product-images/`       | List or create product images      |

**Usage Example:**
```http
GET /api/products/?search=burger&ordering=-price
```
```json
{
  "name": "Burger",
  "price": "5.99",
  "category_id": 1
}
```

---

## Orders

| Method    | Endpoint                              | Description                        |
|-----------|---------------------------------------|------------------------------------|
| GET/POST  | `/api/orders/orders/`                 | List or create orders              |
| GET/PUT/DELETE | `/api/orders/orders/{id}/`        | Retrieve, update, or delete order  |
| POST      | `/api/orders/orders/{id}/pay/`        | Pay for an order                   |
| GET/POST  | `/api/orders/returns/`                | List or create return requests     |
| GET/PUT/DELETE | `/api/orders/returns/{id}/`       | Retrieve, update, or delete return request |
| GET       | `/api/orders/reports/sales-by-product/`| Sales by product report           |
| GET       | `/api/orders/reports/sales-by-date/`  | Sales by date report               |
| GET       | `/api/orders/reports/best-sellers/`   | Best sellers report                |
| GET       | `/api/orders/reports/worst-sellers/`  | Worst sellers report               |
| GET       | `/api/orders/reports/low-stock-alerts/`| Low stock alerts                  |
| GET       | `/api/orders/reports/sales-summary/`  | Sales summary                      |
| GET       | `/api/orders/reports/product-performance/{product_id}/` | Product performance |

**Usage Example:**
```http
POST /api/orders/orders/
{
  "items": [
    {"product_id": 1, "quantity": 2}
  ],
  "delivery_address": "123 Main St"
}
```

---

## Coupons

| Method    | Endpoint                              | Description                        |
|-----------|---------------------------------------|------------------------------------|
| GET/POST  | `/api/coupons/coupons/`               | List or create coupons             |
| GET/PUT/DELETE | `/api/coupons/coupons/{id}/`      | Retrieve, update, or delete coupon |
| POST      | `/api/coupons/coupons/{id}/validate/` | Validate coupon                    |
| POST      | `/api/coupons/coupons/{id}/apply/`    | Apply coupon                       |
| GET/POST  | `/api/coupons/referral-coupons/`      | List or create referral coupons    |
| GET/PUT/DELETE | `/api/coupons/referral-coupons/{id}/` | Retrieve, update, or delete referral coupon |

**Usage Example:**
```http
POST /api/coupons/coupons/2/validate/
{
  "cart_value": "20.00",
  "cart_items": [
    {"product_id": 1, "quantity": 2}
  ]
}
```

---

## Alerts & Notifications

| Method    | Endpoint                              | Description                        |
|-----------|---------------------------------------|------------------------------------|
| GET/POST  | `/api/alerts/alerts/`                 | List or create product alerts      |
| GET/PUT/DELETE | `/api/alerts/alerts/{id}/`        | Retrieve, update, or delete product alert |
| GET/POST  | `/api/alerts/notifications/`          | List or create alert notifications |
| GET/PUT/DELETE | `/api/alerts/notifications/{id}/` | Retrieve, update, or delete alert notification |
| GET       | `/api/alerts/metrics/popularity/`      | Product popularity metrics         |
| GET       | `/api/alerts/metrics/trending/`        | Trending products                  |

**Usage Example:**
```http
POST /api/alerts/alerts/
{
  "product_id": 1,
  "alert_type": "low_stock"
}
```

---

## General Notes

- All endpoints support pagination, filtering, and ordering where applicable.
- Most endpoints require JWT authentication unless otherwise noted.
- For all POST/PUT requests, set `Content-Type: application/json` and include JWT in `Authorization` header if required.
- For detailed request/response formats, see `API.md` or the DRF browsable API. 