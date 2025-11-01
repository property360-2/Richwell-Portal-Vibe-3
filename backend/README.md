# Richwell Portal Backend

This Django project powers the Richwell academic portal. The development settings default to
PostgreSQL via environment variables and expose a `/healthz/` endpoint for readiness checks.

## Local development

```bash
pip install -e .[dev]
python manage.py migrate
python manage.py runserver
```

Visit http://localhost:8000/healthz/ to confirm the application is running.
