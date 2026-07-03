# Finance Django App

Minimal containerized Django project with PostgreSQL and Docker Compose.

## Quick start

1. Copy `.env.example` to `.env` and adjust values if needed.
2. Start the stack:

   ```bash
   docker compose up --build
   ```

3. Open http://localhost:8000

## Local management

To run Django commands inside the container:

```bash
docker compose run --rm web python manage.py createsuperuser
```

## Project layout

- `config/` contains settings, URL routing, and WSGI/ASGI entry points.
- `core/` contains the starter application and homepage view.