# E-Commerce Order Management System

A complete FastAPI backend for managing an e-commerce workflow including users, categories, products, carts, addresses, orders, payments, returns, refunds, reviews, email notifications, and reports.

## Project Overview

The E-Commerce Order Management System provides a RESTful API for managing the complete customer ordering lifecycle.

The application supports:

- User registration and authentication
- JWT-based authentication
- Role-Based Access Control (RBAC)
- Category management
- Product management
- Product search, filtering, sorting, and pagination
- Shopping cart management
- Customer address management
- Order creation and management
- Payment processing
- Order cancellation and refunds
- Product returns
- Product reviews and ratings
- Email notifications
- Sales and order reports
- Low-stock reports
- MySQL database integration
- Alembic database migrations
- Swagger/OpenAPI documentation

## Tech Stack

- Python 3.9+
- FastAPI
- Pydantic
- Pydantic Settings
- SQLAlchemy
- MySQL
- MySQL Connector/Python
- Alembic
- JWT Authentication
- bcrypt
- Uvicorn
- SMTP / smtplib
- FastAPI BackgroundTasks

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
│   │   ├── cart.py
│   │   ├── cart_item.py
│   │   ├── address.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── payment.py
│   │   ├── return_request.py
│   │   └── review.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── address.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── return_request.py
│   │   └── review.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── addresses.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   ├── returns.py
│   │   ├── reviews.py
│   │   └── reports.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── address.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── return_request.py
│   │   └── review.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── email.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── README
│
├── screenshots_output/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

> **Note:** The `.env` file contains local secrets and is intentionally excluded from GitHub using `.gitignore`.

## Authentication

The API provides secure authentication using JWT.

Supported operations:

- User registration
- User login
- JWT access token generation
- Current user information
- Password hashing using bcrypt
- Token expiration
- Protected API endpoints

### User Roles

The application supports:

- `admin`
- `customer`

### Admin

Admins can:

- Manage categories
- Manage products
- Manage orders
- Manage returns
- View reports

### Customer

Customers can:

- Manage their cart
- Manage addresses
- Create orders
- Make payments
- Cancel eligible orders
- Request returns
- Add and manage reviews
- View their orders

## Categories

Supported operations:

- Create category
- List categories
- Get category by ID
- Update category
- Delete category

Category operations are protected according to the user's role.

## Products

Supported operations:

- Create product
- List products
- Get product by ID
- Update product
- Soft delete product
- Search products by name
- Filter products by category
- Sort products
- Pagination
- Stock management
- Active/inactive product validation

Products referenced by existing orders are protected from invalid deletion.

## Shopping Cart

Each customer has one shopping cart.

Supported operations:

- Add product to cart
- View cart
- Update cart item quantity
- Remove cart item
- Clear cart

Business rules include:

- Duplicate products increase the existing quantity.
- Product quantity must be greater than zero.
- Inactive products cannot be added.
- Quantity cannot exceed available stock.
- Cart subtotal is calculated automatically.
- Product prices are taken from the current product price.

## Customer Addresses

Customers can manage delivery addresses.

Supported operations:

- Create address
- List addresses
- Get address
- Update address
- Delete address
- Set default address

Address validation includes:

- Phone number validation
- Pincode validation
- Customer ownership validation
- Only one default address per customer

## Orders

Customers can create orders from their cart.

Supported operations:

- Create order
- List orders
- Get order by ID
- Cancel eligible orders
- Update order status
- View order items

### Order Calculation

Orders automatically calculate:

- Subtotal
- 18% tax
- Delivery charge
- Grand total

Delivery charge:

```text
Subtotal > 500  → Free delivery
Subtotal <= 500 → 50 delivery charge
```

### Order Number

Each order receives a unique order number in the following format:

```text
ORD-XXXXXXXXXXXX
```

### Order Status

The supported order statuses are:

```text
Pending
   ↓
Confirmed
   ↓
Shipped
   ↓
Delivered
```

Orders can also be cancelled when business rules allow it.

Order status can only move forward.

Delivered and cancelled orders cannot be modified.

## Order Business Rules

The API implements the following rules:

- Orders must contain at least one item.
- Product quantity must be greater than zero.
- Orders cannot exceed available stock.
- Stock is deducted during order creation.
- Product price is captured as an order-item price snapshot.
- Order subtotal and total are calculated automatically.
- Shipped orders cannot be cancelled.
- Delivered orders cannot be cancelled or modified.
- Cancelled orders cannot be modified.
- Cancelling an eligible order restores product stock.
- Paid cancelled orders are marked as refunded.
- Database transactions are used for important order operations.
- Failed order operations are rolled back.

## Payments

The payment system supports:

- UPI
- Card
- Net Banking
- COD

Each successful payment receives a unique transaction ID.

Example:

```text
TXN-XXXXXXXXXXXX
```

Payment rules include:

- Payment method validation
- Payment amount must match the order total
- Cancelled orders cannot be paid
- Already-paid orders cannot be paid again
- Successful online payments mark the order as paid
- Successful payments confirm the order
- COD remains unpaid until delivery
- Refunded payments are tracked

## Returns and Refunds

Customers can request returns for eligible orders.

Return rules include:

- Returns are allowed only for delivered orders.
- Return requests must be made within 7 days of delivery.
- Only one return request is allowed per order.
- Admins can approve or reject return requests.
- Rejection requires a reason.
- Approved returns restore product stock.
- Approved returns trigger the applicable refund status.
- Payment status is updated to `Refunded` when applicable.

## Reviews and Ratings

Customers can review products purchased through delivered orders.

Review rules include:

- Product must belong to a delivered order of the customer.
- A customer can review a product only once.
- Customers can edit their own reviews.
- Customers can delete their own reviews.
- Product average rating is maintained.
- Product review count is maintained.

## Email Notifications

The application supports email notifications using SMTP and FastAPI background tasks.

Emails can be triggered for:

- User registration
- Order creation
- Successful payment
- Order shipped
- Order delivered
- Order cancellation
- Return approval
- Return rejection

SMTP configuration is provided through environment variables.

## Reports

Admin reporting endpoints provide information such as:

- Sales report
- Orders by status
- Top 5 products
- Low-stock products

These endpoints are protected using admin role authorization.

## Database

The application uses MySQL with SQLAlchemy.

Database:

```text
ecommerce_order_db
```

Database operations are managed through SQLAlchemy sessions.

## Database Migrations

Alembic is used for database migrations.

Example commands:

```bash
alembic upgrade head
```

To create a new migration:

```bash
alembic revision --autogenerate -m "migration message"
```

## Environment Configuration

Create a local `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=mysql+mysqlconnector://root:password@localhost:3306/ecommerce_order_db

JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

> Never commit the `.env` file to GitHub.

## Installation

Clone the repository:

```bash
git clone https://github.com/srinivasulu3679/E-Commerce-Order-Management-System.git
```

Move into the project directory:

```bash
cd E-Commerce-Order-Management-System
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the `.env` file with the local MySQL database and required settings.

Run database migrations:

```bash
alembic upgrade head
```

## Running the Application

Start the FastAPI application using:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Swagger Documentation

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Alternative ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

Swagger can be used to test authentication, products, carts, addresses, orders, payments, returns, reviews, and reports.

## Security

The application uses:

- JWT authentication
- Password hashing with bcrypt
- Role-based authorization
- Protected customer resources
- Protected admin resources
- Environment variables for secrets
- Database validation and transactions

## Screenshots

The project includes API testing screenshots demonstrating important application workflows using Swagger/OpenAPI.

The screenshots cover key functionality such as:

- Authentication
- Categories
- Products
- Cart
- Addresses
- Orders
- Payments
- Other important business workflows

## GitHub Repository

Repository:

https://github.com/srinivasulu3679/E-Commerce-Order-Management-System

## Conclusion

The E-Commerce Order Management System provides a complete FastAPI backend implementing authentication, authorization, product and cart management, order processing, payments, returns, refunds, reviews, email notifications, reporting, database migrations, and real-world business validations.
