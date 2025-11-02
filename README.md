# Richwell College Portal v3.0

This repository contains the Django implementation of the Richwell College Portal. The project embraces an archive-first
academic workflow, consolidating enrollment, grade encoding, and analytics into a single interface rendered with Django
templates.

## Getting started

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the environment template and adjust as needed:

   ```bash
   cp .env.example .env
   ```

3. Run migrations and start the development server:

   ```bash
   python backend/manage.py migrate
   python backend/manage.py runserver
   ```

4. Visit <http://127.0.0.1:8000/> for the landing page and <http://127.0.0.1:8000/healthz/> for the health check endpoint.

## Testing

Execute the project's tests with:

```bash
python backend/manage.py test core
```

The command targets the installed Django apps and ensures the health check and landing page render successfully.
