# E-Commerce Order Management API

A professional FastAPI backend for managing users, categories, products, and customer orders.

## Project Overview

The E-Commerce Order Management API provides a RESTful backend for managing an e-commerce workflow.

The application supports:

* User registration and authentication
* JWT-based authentication
* Role-Based Access Control (RBAC)
* Category management
* Product management
* Product search and filtering
* Product stock management
* Customer order creation
* Order item management
* Order status management
* Order filtering and pagination
* Business validations
* MySQL database integration
* Alembic database migrations
* Swagger/OpenAPI documentation

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* MySQL
* MySQL Connector/Python
* Pydantic
* Pydantic Settings
* Alembic
* JWT
* bcrypt
* Uvicorn

## Project Structure

```text
E_Commerce_Order_Management/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── order_item.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── order.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── products.py
│   │   └── orders.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   └── order_service.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── validators.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── README
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## Features

### Authentication

* User registration
* User login
* JWT access tokens
* Current user information
* Password hashing using bcrypt
* Token expiration
* Protected API endpoints

### Role-Based Access Control

The application supports:

* `admin`
* `customer`

Admin users can manage categories and products.

Customer users can access customer-level functionality but cannot perform admin-only operations.

### Categories

Supported operations:

* Create category
* List categories
* Get category by ID
* Update category
* Delete category

### Products

Supported operations:

* Create product
* List products
* Get product by ID
* Update product
* Delete product
* Search products by name
* Filter products by category
* Pagination
* Stock management

### Orders

Supported operations:

* Create order
* List orders
* Get order by ID
* Update order status
* Filter by order status
* Filter by customer email
* Pagination
* Order item management
* Automatic subtotal calculation
* Automatic total calculation
* Stock validation
* Stock deduction after order creation

## Order Status Flow

Orders support the following statuses:

```text
pending
   ↓
confirmed
   ↓
shipped
   ↓
delivered
```

Orders can also be cancelled when business rules allow it.

Delivered and cancelled orders cannot be updated.

## Business Validations

The API implements several business rules:

* Duplicate product items are not allowed in the same order.
* Orders must contain at least one item.
* Product quantity must be greater than zero.
* Orders cannot exceed available product stock.
* Product stock is automatically reduced after order creation.
* Product prices are captured at the time of order creation.
* Shipped orders cannot be cancelled.
* Delivered orders cannot be modified.
* Cancelled orders cannot be modified.
* Products referenced by existing orders cannot be deleted.
* Category references are validated before product creation/update.
* Duplicate user email addresses are prevented.
* Protected admin endpoints require an admin role.

## Database

The application uses MySQL.

Database name:

```text
ecommerce_order_db
```

Main tabl
