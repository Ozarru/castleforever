# CastleForever VPS deployment

> For the Docker Compose staging/production setup, see
> [`DEPLOYMENT_DOCKER.md`](DEPLOYMENT_DOCKER.md). This guide covers a
> non-containerised systemd + Nginx deployment.

This guide deploys the project to a single Ubuntu 22.04/24.04 VPS with:

- **Gunicorn** (systemd service) running the Django app
- **Nginx** as TLS-terminating reverse proxy and static-file server
- **PostgreSQL** as the database
- **Let's Encrypt (Certbot)** for HTTPS
- **S3-compatible object storage** for uploaded media

Static assets stay on the VPS (`staticfiles/`). Only user uploads (venues,
vehicles, etc.) go to the bucket.

---

## 1. Prerequisites

- A VPS with a public IPv4 address and sudo access.
- A domain (e.g. `example.com`) with `A`/`AAAA` records pointing to the VPS.
- An S3-compatible bucket. Supported examples:

| Provider      | Endpoint                                          | Region                  |
| ------------- | ------------------------------------------------- | ----------------------- |
| AWS S3        | *(leave empty)*                                 | e.g. `eu-west-3`      |
| Cloudflare R2 | `https://<account-id>.r2.cloudflarestorage.com` | `auto`                |
| Backblaze B2  | `https://s3.<region>.backblazeb2.com`           | e.g. `eu-central-003` |
| Wasabi        | `https://s3.<region>.wasabisys.com`             | e.g. `eu-central-1`   |
| MinIO         | `https://minio.example.com`                     | *(empty)*             |

Create a bucket and an access key limited to that bucket.

---

## 2. System packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  python3 python3-venv python3-dev build-essential \
  libpq-dev postgresql postgresql-contrib \
  nginx git curl \
  certbot python3-certbot-nginx
```

---

## 3. Application user and code

```bash
sudo adduser --system --group --home /srv/castleforever castleforever
sudo usermod -aG www-data castleforever

sudo mkdir -p /srv/castleforever
sudo chown castleforever:castleforever /srv/castleforever

sudo -u castleforever git clone <YOUR_REPO_URL> /srv/castleforever
cd /srv/castleforever

sudo -u castleforever python3 -m venv .venv
sudo -u castleforever .venv/bin/pip install --upgrade pip
sudo -u castleforever .venv/bin/pip install -r requirements.txt
```

> If `/srv/castleforever` already exists (e.g. empty directory), clone into it
> with `git clone <URL> .` instead.

---

## 4. PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE castleforever;
CREATE USER castleforever WITH ENCRYPTED PASSWORD 'choose-a-strong-password';
ALTER ROLE castleforever SET client_encoding TO 'utf8';
ALTER ROLE castleforever SET default_transaction_isolation TO 'read committed';
ALTER ROLE castleforever SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE castleforever TO castleforever;
ALTER DATABASE castleforever OWNER TO castleforever;
\q
```

The resulting `DATABASE_URL` is:

```text
postgres://castleforever:choose-a-strong-password@127.0.0.1:5432/castleforever
```

---

## 5. Environment file

```bash
cd /srv/castleforever
sudo -u castleforever cp .env.example .env
sudo -u castleforever nano .env
sudo chmod 600 .env
```

At minimum set:

- `DJANGO_SECRET_KEY` — generate with
  `python3 -c "from django.core.management.utils import get_random_secret_key as k; print(k())"`
- `DJANGO_ALLOWED_HOSTS=example.com,www.example.com`
- `CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com`
- `DATABASE_URL`
- `USE_S3_MEDIA=1` and the `S3_*` values for your provider

`.env` is loaded by `config/settings.py`; real environment variables always
take precedence over it.

### Bucket access model

Two common setups:

1. **Public bucket + CDN/custom domain (recommended for image-heavy sites)**
   - `S3_QUERYSTRING_AUTH=0`
   - `S3_CUSTOM_DOMAIN=cdn.example.com` (or the provider's public hostname)
   - Expose the bucket publicly via bucket policy or the provider's public
     access setting. Do **not** set `S3_DEFAULT_ACL=public-read` on AWS buckets
     where ACLs are disabled — use a bucket policy instead.
2. **Private bucket with signed URLs**
   - `S3_QUERYSTRING_AUTH=1`
   - Leave `S3_CUSTOM_DOMAIN` empty.
   - URLs expire, so they are not suitable for long-lived CDN caching.

If neither is configured, Django falls back to local `media/` storage.

---

## 6. First deploy

```bash
cd /srv/castleforever
sudo -u castleforever .venv/bin/python manage.py migrate --noinput
sudo -u castleforever .venv/bin/python manage.py collectstatic --noinput
sudo -u castleforever .venv/bin/python manage.py createsuperuser
```

Do **not** run `seed_catalog` on every production deploy — it is demo data.
`build.sh` is the Render build script and is not used on the VPS.

---

## 7. Gunicorn systemd service

```bash
sudo cp deploy/castleforever.service /etc/systemd/system/castleforever.service
sudo systemctl daemon-reload
sudo systemctl enable --now castleforever
sudo systemctl status castleforever
```

Logs:

```bash
sudo journalctl -u castleforever -f
```

The service listens on `/run/castleforever/gunicorn.sock`.

If you use a different path/user, edit `deploy/castleforever.service` before
copying it (and the Nginx paths below).

---

## 8. Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/castleforever
sudo ln -s /etc/nginx/sites-available/castleforever /etc/nginx/sites-enabled/castleforever
sudo rm -f /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-available/castleforever   # replace example.com
sudo nginx -t
sudo systemctl reload nginx
```

The config already:

- passes `X-Forwarded-Proto` so Django's HTTPS redirect and cookies work
- serves `/static/` from `/srv/castleforever/staticfiles/`
- proxies `/healthz/` (used by `deploy/deploy.sh`)
- allows uploads up to 25 MB (`client_max_body_size`)

`/media/` is only served locally. With a bucket, media URLs point directly at
the bucket/CDN.

---

## 9. HTTPS with Let's Encrypt

```bash
sudo certbot --nginx -d example.com -d www.example.com
sudo systemctl list-timers | grep certbot   # automatic renewal
```

Then confirm:

```bash
curl -I https://example.com/healthz/
```

Django also enforces HSTS and HTTPS redirects when `DJANGO_DEBUG=0`. If you
need to debug over plain HTTP, temporarily set `DJANGO_SECURE_SSL_REDIRECT=0`
and `DJANGO_HSTS_SECONDS=0`, then restart the service.

---

## 10. Redeploying

```bash
cd /srv/castleforever
chmod +x deploy/deploy.sh   # once
./deploy/deploy.sh
```

The script pulls the latest code, installs dependencies, migrates, collects
static files, restarts Gunicorn and verifies `/healthz/`. It can be run as root
or as `castleforever`; internal commands are executed as `castleforever`.
Override `APP_USER`, `APP_DIR` or `SERVICE_NAME` if your setup differs. Set
`HEALTHCHECK_HOST` if the domain is not `example.com`:

```bash
HEALTHCHECK_HOST=your-domain.com ./deploy/deploy.sh
```

---

## 11. Moving existing uploads into the bucket

If the site already has files in `media/`, copy them before switching:

```bash
# AWS CLI v2 example
aws s3 sync /srv/castleforever/media/ s3://castleforever-media/media/ \
  --endpoint-url "$S3_ENDPOINT_URL"
```

For R2/MinIO, the AWS CLI works with `--endpoint-url`; `rclone` is a good
alternative. Keep `S3_LOCATION=media` so database paths remain valid — the
stored values are relative (e.g. `venues/castle.jpg`).

After copying, set `USE_S3_MEDIA=1`, restart the service, and verify that
existing images load and that a new admin upload succeeds.

---

## 12. Backups and maintenance

- **Database:** `pg_dump castleforever > backup.sql` on a cron/systemd timer,
  stored off the VPS.
- **Bucket:** enable versioning or lifecycle rules at the provider.
- **Static files:** regenerated by `collectstatic`; no backup needed.
- **Logs:** `journalctl -u castleforever` (or ship to a log service).
- **Certificates:** renewed automatically by the Certbot timer.

---

## 13. Troubleshooting

| Symptom                              | Check                                                                                                                      |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| `502 Bad Gateway`                  | `sudo systemctl status castleforever`, then journal logs. Ensure the socket exists and `Group=www-data` matches Nginx. |
| Static files 404                     | `collectstatic` ran, `STATIC_ROOT=/srv/castleforever/staticfiles`, Nginx `alias` path correct.                       |
| Uploads 403/500                      | Bucket credentials, endpoint URL, region, bucket policy/ACL, and whether the key allows `s3:PutObject`.                  |
| Images 404 after switching to bucket | Files were not copied, or `S3_LOCATION` differs from the prefix used when copying.                                       |
| `DisallowedHost`                   | Add the domain to `DJANGO_ALLOWED_HOSTS` and restart.                                                                    |
| CSRF verification failed             | Add the exact HTTPS origin to `CSRF_TRUSTED_ORIGINS`.                                                                    |
| Redirect loop                        | Nginx must send `X-Forwarded-Proto $scheme`; check `SECURE_PROXY_SSL_HEADER`.                                          |
