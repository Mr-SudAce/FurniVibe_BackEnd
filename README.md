# FurniVibe API & Dashboard

FurniVibe is a robust Django-based e-commerce backend designed for furniture retail. It features a comprehensive REST API for client applications and a dedicated server-side dashboard for inventory and order management.

## 🚀 Features

### Core Functionality
- **Product Management:** Full CRUD for Products, Categories, Brands, and Product Variants (Color/Material).
- **Order System:** Cart management, Order placement, Order tracking, and History.
- **Authentication:** 
  - **API:** JWT (JSON Web Token) via `simplejwt` for secure stateless client authentication.
  - **Dashboard:** Session-based authentication for staff access.
- **Content Management:** Blog posts and additional product imagery.

### Staff Dashboard
- **Role-Based Access:** Protected views for Staff and Superadmins.
- **Inventory Control:** Visual interfaces to add/edit products and variants.
- **Order Processing:** Admin views to update order status and payment status.
- **Statistics:** Basic sales and order counters on the home dashboard.

### API Documentation
- Integrated **Swagger/OpenAPI** documentation using `drf-spectacular`.

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Framework:** Django 5.x
- **API Toolkit:** Django REST Framework (DRF)
- **Authentication:** SimpleJWT & Django Auth
- **Documentation:** drf-spectacular
- **Utilities:** django-filter, django-cors-headers, python-dotenv

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd B_furniVibe
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
*(Note: Ensure you generate a requirements.txt if not present)*
```bash
pip install django djangorestframework djangorestframework-simplejwt django-filter drf-spectacular django-cors-headers django-tinymce python-dotenv Pillow
```

### 4. Environment Configuration
Create a `.env` file in the root directory (`B_furniVibe/`) and add the following configurations:

```env
SECRET_KEY=your-super-secret-key-here
DEBUG=True

# Optional: Default Superadmin Credentials
DEFAULT_SUPERADMIN_USERNAME=superadmin
DEFAULT_SUPERADMIN_EMAIL=admin@example.com
DEFAULT_SUPERADMIN_PASSWORD=admin12345
```

### 5. Database Setup
Run migrations to create the SQLite database schema.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser
To access the Dashboard and Django Admin:
```bash
python manage.py createsuperuser
```

## 🏃‍♂️ Running the Server

```bash
python manage.py runserver
```

Access the application at: `http://127.0.0.1:8000/`

## 📚 API Documentation

Once the server is running, you can explore the API endpoints via the interactive Swagger UI:

- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **Schema:** `http://127.0.0.1:8000/api/schema/`

## 📂 Project Structure

```text
B_furniVibe/
├── api_app/             # Main application logic
│   ├── models.py        # Database models
│   ├── api_views.py     # DRF API Views
│   ├── dashboard_views.py # Staff Dashboard Views
│   ├── serializers.py   # API Serializers
│   └── urls.py          # App specific URLs
├── api_main/            # Project settings
│   ├── settings.py      # Main configuration
│   └── urls.py          # Root URL routing
├── Handler/             # Custom utility handlers (Views, API, etc.)
├── media/               # User uploaded files (Images)
├── manage.py            # Django command-line utility
└── requirements.txt     # Python dependencies
```