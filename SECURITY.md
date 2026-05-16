# Security Policy

## Supported Versions

This is a **development / portfolio** project. Security fixes are applied on the `main` branch.

## Reporting a Vulnerability

If you discover a security issue, please open a private report or email the maintainer instead of filing a public issue with exploit details.

## Deployment Checklist

Before exposing this app to the internet:

1. Set `DEBUG=False` and a strong `SECRET_KEY`.
2. Set `SITE_URL` to your public HTTPS origin.
3. Set `ENABLE_API_DOCS=False` unless docs should be public.
4. Configure `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS`.
5. Do not expose PostgreSQL or Redis ports publicly.
6. Use a real SMTP provider and TLS for email.
