# AR Handlooms E-Commerce Platform

A professional, production-ready e-commerce website built with Django, featuring a modern UI/UX, customer accounts, order management, and administrative dashboard.

## Features

- **Storefront**: Browse products by category, search functionality, and detailed product views.
- **Cart & Wishlist**: Seamless shopping experience with AJAX-ready cart updates.
- **Checkout**: Secure checkout process with account creation options.
- **Customer Dashboard**: Track orders, manage profile, and change passwords.
- **Admin Dashboard**: Comprehensive analytics, product/category management, and order tracking.
- **Production Ready**: Configured with Whitenoise, environment variables, and security best practices.

## Modern UI/UX

- Theming inspired by premium fashion stores.
- Modern typography using **Outfit** and **Playfair Display**.
- Fully responsive design for all devices.
- Smooth transitions and interactive elements.

## Getting Started

### 1. Prerequisites
- Python 3.x
- MySQL (optional, defaults to SQLite if not configured)

### 2. Setup
1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`.
3. Activate the virtual environment.
4. Install dependencies: `pip install -r requirements.txt`.
5. Create a `.env` file based on `.env.example` and fill in your details.
6. Run migrations: `python manage.py migrate`.
7. Create a superuser: `python manage.py createsuperuser`.
8. Start the development server: `python manage.py runcommand`.

## Deployment

The project is configured for deployment on platforms like **Render**, **Heroku**, or **DigitalOcean**.

### Steps:
1. Set the following environment variables on your hosting platform:
   - `SECRET_KEY`: A long, random unique string.
   - `DEBUG`: Set to `False`.
   - `ALLOWED_HOSTS`: Your domain name (e.g., `yourproject.onrender.com`).
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Your production database credentials.
2. The project uses **Whitenoise** to serve static files automatically.
3. Ensure you collect static files during the build process: `python manage.py collectstatic --no-input`.

## License
MIT License.