# Mission3
## Django Image Upload App

A responsive Django web application for users to upload images with validation, drag-and-drop support, and a custom Django Admin for reviewing submissions.

## Features
- Mobile-friendly Bootstrap 5 UI
- Drag-and-drop upload with image preview
- Server-side validation for file types (JPG, PNG, WebP) and max size (10MB)
- Custom Django admin with image thumbnails and status management

## Setup Instructions

1. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser for the admin**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000/` to view the app, and `http://127.0.0.1:8000/admin/` to view the admin panel.
