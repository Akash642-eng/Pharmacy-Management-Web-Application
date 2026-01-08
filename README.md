# 🏥 Maruti Pharmacy Management System

A modern, modular **Flask-based web application** built to manage pharmacy operations efficiently.  
This project focuses on **clean backend architecture**, **domain separation**, and **production-ready design practices**.

---

# 📌 Project Overview

Pharmacy systems require accuracy, security, and scalability.  
This project implements a **pharmacy management platform** that handles authentication, product management, cart workflows, order processing, and payment abstraction using a well-structured Flask architecture.

The application is designed to reflect **real-world backend engineering standards**, not just a basic CRUD setup.

---

# 🎯 Objectives

- Design a scalable Flask backend using Blueprints
- Implement secure user authentication
- Manage products, carts, and orders cleanly
- Abstract payment and notification logic
- Follow clean architecture and separation of concerns
- Build a GitHub-ready, production-style project

---

# 🧠 Application Architecture

- **Architecture Style**: Modular Flask (Blueprint-based)
- **Design Principle**: Domain-driven separation
- **Application Pattern**: Application Factory Pattern

Each module represents a real business domain such as authentication, products, orders, and payments.

---

# 📂 Project Structure

maruti-pharmacy/
│
├── app/
│   ├── admin/            # Admin-level operations
│   ├── auth/             # Authentication and authorization
│   ├── cart/             # Cart management logic
│   ├── gateway/          # External service integration layer
│   ├── main/             # Public-facing routes
│   ├── notifications/    # System notifications
│   ├── orders/           # Order lifecycle management
│   ├── payments/         # Payment abstraction
│   ├── products/         # Product and inventory management
│   │
│   ├── static/           # CSS, JavaScript, images
│   ├── templates/        # Jinja2 templates
│   │
│   ├── __init__.py       # Application factory
│   ├── config.py         # Centralized configuration
│   └── extensions.py    # Flask extensions initialization
│
├── instance/
│   └── maruti.db         # SQLite database
│
├── migrations/           # Database migrations
│
├── venv/                 # Virtual environment
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── run.py                # Application entry point

---

# 🧩 Module Responsibilities

- **Auth Module**
Handles user login, logout, and session management with secure password hashing.

- **Admin Module**
Contains admin-only routes and restricted operations.

- **Products Module**
Manages pharmacy products and inventory data.

- **Cart Module**
Handles temporary cart operations before order placement.

- **Orders Module**
Manages order creation, storage, and status tracking.

- **Payments Module**
Abstracts payment processing logic for future integrations.

- **Gateway Module**
Acts as a boundary for external services and APIs.

- **Notifications Module**
Handles system notifications such as order confirmations.

- **Main Module**
Contains public and landing page routes.


## 🛠 Technologies Used

- Python 🐍
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Bcrypt
- Flask-Migrate
- SQLite (Configurable)

## ⚙️ Application Workflow

1. User authentication and session handling
2. Product browsing and selection
3. Cart management
4. Order creation
5. Payment processing abstraction
6. Notification handling
7. Persistent storage using database

## 🚀 How to Run the Project
**Step 1: Clone the repository**

  git clone https://github.com/your-username/maruti-pharmacy.git
  cd maruti-pharmacy

**Step 2: Create and activate virtual environment**

  python -m venv venv
  venv\Scripts\activate

**Step 3: Install dependencies**

  pip install -r requirements.txt

## 🔧 Environment Setup

**Create a .env file in the root directory**

FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///maruti.db

**🗄 Database Initialization**

flask db init
flask db migrate -m "Initial migration"
flask db upgrade

## ▶️ Run the Application

- flask run

**Application runs at**

- http://127.0.0.1:5000

## 📄 License

- This project is created for learning, demonstration, and portfolio purposes.


