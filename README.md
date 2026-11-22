# CastleForever

A lean Django 5.2 project with four apps:

- `accounts`  -  custom User, Django Groups and Permissions, login/logout.
- `catalog`  -  estates, estate photos, vehicles, estate detail pages.
- `core`  -  booking enquiries, vehicle rentals, proposed estate payment schedules.
- `base`  -  public homepage and shared templates.

## Local setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations accounts catalog core
python manage.py migrate
python manage.py seed_catalog
python manage.py seed_marketing
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/ and create published estates. The homepage displays those estates automatically. Upload optional photos or supply remote image URLs.

**Important:** Generate and commit the initial migrations before production deployment. Do not change `AUTH_USER_MODEL` after creating the database.

## Scope

- Estate enquiry forms save records to the database; they do not confirm bookings.
- The public `/reviews/`, `/results/` and `/appointment/` pages are marketing pages backed by the `Testimonial`, `EventRecord` and `Appointment` models. Run `python manage.py seed_marketing` to load the demo reviews and 2025 figures, then replace them with verified data in the admin.
- Appointment requests are stored for staff follow-up; they are not synced to an external calendar.
- Vehicle rental and payment schedule models exist for admin-managed workflows; online checkout, availability locking, financing approvals, and automatic installments are **not implemented**.
- Installment examples are nonbinding, assume no interest or fees, and apply only to estate rentals. Vehicle rentals require full payment.
- Estate prices and remote photos must be populated with verified, licensed real listings before launch.
- Tailwind is compiled at build time into `static/tailwind.css` (no browser-side CDN). After changing any template class, run `npm install && npm run build:css` and commit the regenerated file. Review remote image licensing before launch.
- For production, set `DJANGO_DEBUG=0`, a strong `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS`. Use a production database, HTTPS and appropriate static/media hosting.

## Deploying with Docker Compose

See [`DEPLOYMENT_DOCKER.md`](DEPLOYMENT_DOCKER.md) for staging and production
Docker Compose deployments. Each environment uses its own env file
(`.env.stage` / `.env.prod`), Compose project, database volume and host port:

```bash
./deploy/compose.sh stage up -d --build
./deploy/compose.sh prod up -d --build
```

## Deploying to a VPS (without Docker)

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for a full Ubuntu + Nginx + Gunicorn +
PostgreSQL + Certbot setup. Uploaded media is stored in an S3-compatible bucket
when `USE_S3_MEDIA=1`; `.env.example` documents the relevant variables.
Helper files live in `deploy/`.

## Deploying to Render.com

This project ships with a `render.yaml` blueprint and a `build.sh` script.

1. Push the repository to GitHub/GitLab/Bitbucket.
2. In Render, choose **New > Blueprint** and select the repository. Render will create the web service and PostgreSQL database defined in `render.yaml`.
3. Render automatically sets `DATABASE_URL`, `RENDER_EXTERNAL_HOSTNAME`, and a generated `DJANGO_SECRET_KEY`. Add any extra values (e.g. `CSRF_TRUSTED_ORIGINS`) in the service's **Environment** tab.
4. The build runs `bash build.sh`, which installs dependencies, runs `collectstatic`, applies migrations, and seeds the catalog.
5. The service starts with `gunicorn config.wsgi:application`.

Notes:
- Uploaded media is stored on the instance's ephemeral filesystem by default and will not persist across deploys/restarts. Set `USE_S3_MEDIA=1` plus the `S3_*` variables to use an S3-compatible bucket (see `.env.example`).
- To create an admin user, open the Render shell and run `python manage.py createsuperuser`.
