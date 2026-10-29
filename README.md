# Django Real Estate Backend

A REST API for a real estate listings app, built with Django and Django REST Framework. Realtors register, log in with JWT, and manage their own property listings. Anyone can browse and search published listings.

## Purpose

A learning project to explore Django, cloud storage (AWS S3) and full-stack frameworks. I tried S3 for image storage, then removed it to avoid cloud billing risk, so uploads are stored locally. A frontend is planned (see the roadmap).

## Features

- **JWT authentication** (login, refresh, verify) using `djangorestframework-simplejwt`
- **Custom user model** with email login and an `is_realtor` role
- **Realtor-only listing management**: create, read, update, publish/unpublish and delete your own listings
- **Public endpoints** to list and search published listings (price, bedrooms, bathrooms, sale type, home type)
- **Two databases** (users and listings) using Django database routers
- **Image uploads** stored in a local `media/` folder
- **Django admin** for listings

## Tech stack

Python, Django, Django REST Framework, SimpleJWT, PostgreSQL, Pillow

## API endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/user/register` | Public | Create a user or realtor account |
| GET | `/auth/user/me` | JWT | Get the logged-in user's details |
| POST | `/api/token/` | Public | Log in, get access and refresh tokens |
| POST | `/api/token/refresh/` | Public | Get a new access token |
| POST | `/api/token/verify/` | Public | Check a token is valid |
| GET | `/api/listing/get-listings` | Public | All published listings, newest first |
| GET | `/api/listing/search` | Public | Search and filter published listings |
| GET | `/api/listing/detail?slug=...` | JWT | One published listing |
| GET / POST / PUT / PATCH / DELETE | `/api/listing/manage` | JWT (realtor) | Manage your own listings |

Send the access token as `Authorization: Bearer <token>`.

## Getting started

### 1. Clone and install

```bash
git clone https://github.com/MatroseMzwandile/Django-Real-Estate-Backend-App.git
cd Django-Real-Estate-Backend-App
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create a `.env` file

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/users_db
LISTINGS_DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/listings_db
```

`.env` is in `.gitignore`. Never commit it.

### 3. Migrate both databases and run

```bash
python manage.py migrate --database=users
python manage.py migrate --database=listings
python manage.py createsuperuser
python manage.py runserver
```

## Project structure

```
core/       project settings and root URLs
user/       custom user model, registration, JWT user details, auth DB router
listing/    listing model, views, serializers, admin, listings DB router
```

## What I learned

<!-- Replace with your own words. Examples of what you could cover: -->
- How Django database routers send different apps to different databases
- Building a custom user model that logs in with email
- Securing endpoints with JWT and role checks
- Using S3 for media storage, and why I removed it (cost control)

## Roadmap

Tracked in [Issues](../../issues). Main items:

- [ ] Fix search and sale/home type bugs
- [ ] Restrict who can register as a realtor
- [ ] Add automated tests
- [ ] Move validation into DRF serializers
- [ ] Add API documentation (Swagger / OpenAPI)
- [ ] Build a frontend (Next.js or React)
- [ ] Docker support

## Author

Mzwandile Matrose, software engineering student at WeThinkCode_.
[LinkedIn](https://www.linkedin.com/in/mzwandile-matrose)
