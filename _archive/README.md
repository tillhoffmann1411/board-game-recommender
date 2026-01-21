# Archived Code

This directory contains legacy code from the original Django/Angular implementation.
Archived on: 2026-01-15

## Contents

- `backend/` - Django REST API (Django 3.0 + DRF)
- `frontend/` - Angular 11 application
- `scripts/` - Deployment scripts
- `docker-compose.yml` - Original development compose
- `docker-compose.prod.yml` - Original production compose
- `recommendation-algorithms/` - Extracted recommendation algorithms for porting
- `django-models/` - Extracted Django models for MongoDB schema reference

## Why Archived?

The project is being rebuilt with:
- Next.js (replacing Django + Angular)
- MongoDB (replacing PostgreSQL)
- Clerk Auth (replacing JWT)

## Reference Materials

The `recommendation-algorithms/` and `django-models/` directories contain code
that will be ported to the new system. Refer to these when implementing:
- Recommendation engine in TypeScript/Python
- MongoDB schema design
