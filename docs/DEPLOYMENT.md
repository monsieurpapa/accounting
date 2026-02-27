# Deployment Guide

This document outlines production deployment considerations for the Accounting System.

---

## Table of Contents

1. [Production Checklist](#production-checklist)
2. [Environment Variables](#environment-variables)
3. [Docker Deployment](#docker-deployment)
4. [Static & Media Files](#static--media-files)
5. [Database](#database)
6. [Security](#security)
7. [Monitoring & Logging](#monitoring--logging)

---

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set a strong, unique `SECRET_KEY`
- [ ] Configure `DJANGO_ALLOWED_HOSTS` with production domains
- [ ] Use PostgreSQL (not SQLite)
- [ ] Configure HTTPS (Nginx or reverse proxy)
- [ ] Run `collectstatic --noinput`
- [ ] Set secure database and Redis credentials
- [ ] Configure email backend for password reset
- [ ] Review CSRF and CORS settings
- [ ] Enable Django security middleware and checks

---

## Environment Variables

| Variable | Production Value | Notes |
|----------|------------------|-------|
| `DEBUG` | `False` | **Required** – prevents sensitive data leakage |
| `SECRET_KEY` | Long random string | Use `openssl rand -hex 32` |
| `DJANGO_ALLOWED_HOSTS` | `yourdomain.com www.yourdomain.com` | Comma or space-separated |
| `DATABASE_URL` | `postgres://user:pass@host:5432/db` | Use SSL in production |
| `CELERY_BROKER_URL` | Redis URL | Same as dev or dedicated Redis |
| `DJANGO_EMAIL_BACKEND` | SMTP backend | For password reset, notifications |
| `DEFAULT_FROM_EMAIL` | `noreply@yourdomain.com` | Outgoing email address |

---

## Docker Deployment

1. **Build and start**:
   ```bash
   docker-compose up -d
   ```

2. **Migrations**:
   ```bash
   docker-compose exec app python manage.py migrate
   ```

3. **Static files**:
   ```bash
   docker-compose exec app python manage.py collectstatic --noinput
   ```

4. **Superuser** (if needed):
   ```bash
   docker-compose exec app python manage.py createsuperuser
   ```

5. **Health checks**: Ensure HAProxy and Nginx are healthy; monitor logs with `docker-compose logs -f`.

---

## Static & Media Files

- **Static**: Collected via `collectstatic`; served by Nginx (or CDN in high-traffic setups)
- **Media**: User uploads; ensure volume persistence and backups
- **Nginx**: Configure `location /static/` and `location /media/` in Nginx config

---

## Database

- Use PostgreSQL in production; avoid SQLite
- Enable SSL for `DATABASE_URL` if DB is remote
- Regular backups; test restore process
- Run migrations during deployment; consider blue-green for zero-downtime

---

## Security

- **HTTPS**: Terminate SSL at Nginx; use `SECURE_PROXY_SSL_HEADER`
- **Headers**: Add security headers (HSTS, X-Content-Type-Options, etc.) in Nginx
- **CORS**: Configure `django-cors-headers` if API is consumed by another domain
- **Secrets**: Store in env or secret manager; never commit `.env`
- **Django checks**: Run `python manage.py check --deploy` before deploy

---

## Monitoring & Logging

- **Logging**: Configure `LOGGING` in settings; send logs to stdout or external service
- **Error tracking**: Integrate Sentry or similar for exception reporting
- **Health endpoint**: Add `/health/` or `/ping/` for load balancer checks
- **Celery**: Monitor worker and beat; set up alerts for failed tasks
