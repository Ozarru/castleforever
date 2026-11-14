# Docker Compose deployment

The project runs as two independent Docker Compose projects on the same (or
separate) VPS:

| Environment | Compose project | Env file | Host port | Domain |
| --- | --- | --- | --- | --- |
| Staging | `castleforever-stage` | `.env.stage` | `127.0.0.1:8001` | `stage.castleforever.com` |
| Production | `castleforever-prod` | `.env.prod` | `127.0.0.1:8000` | `castleforever.com` |

Each project has its own `web` container, PostgreSQL container and named
volumes (`postgres_data`, `media_data`), so the two environments never share
data.

- **Gunicorn** serves Django inside the `web` container.
- **WhiteNoise** serves collected static files through Gunicorn, so no separate
  static volume/container is required.
- **Uploaded media** is stored in the S3-compatible bucket in production. Staging
  defaults to the local `media_data` volume.
- **Nginx on the host** terminates TLS and proxies to the container ports.
  Certbot is still the simplest way to manage certificates.

> `.env.stage` and `.env.prod` are git-ignored and contain real credentials.
> Keep them on the server only, owned by the deploy user with mode `600`.

---

## 1. Prerequisites

- Ubuntu 22.04/24.04 VPS (or any Linux host with Docker).
- Docker Engine 24+ with the Compose v2 plugin.
- A domain with DNS records for both environments.
- An S3-compatible bucket for production (and optionally staging).

Install Docker:

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
# log out/in (or `newgrp docker`) so the group applies
docker compose version
```

---

## 2. Get the project

```bash
sudo mkdir -p /opt/castleforever
sudo chown "$USER":"$USER" /opt/castleforever
git clone <YOUR_REPO_URL> /opt/castleforever
cd /opt/castleforever
```

`.env.stage` and `.env.prod` are intentionally git-ignored. On a fresh server
they must be created once (for example from `.env.example`) and filled in with
the values below, then locked down:

```bash
chmod 600 .env.stage .env.prod
chmod +x deploy/compose.sh
```

### Required values in both files

```env
ENV_FILE=.env.stage              # or .env.prod
COMPOSE_PROJECT_NAME=castleforever-stage
APP_PORT=8001                    # 8000 for prod
GUNICORN_WORKERS=3

DJANGO_SECRET_KEY='...'
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=stage.castleforever.com,www.stage.castleforever.com
CSRF_TRUSTED_ORIGINS=https://stage.castleforever.com,https://www.stage.castleforever.com
POSTGRES_DB=castleforever
POSTGRES_USER=castleforever
POSTGRES_PASSWORD=...
DATABASE_URL=postgres://castleforever:...@db:5432/castleforever

USE_S3_MEDIA=1
S3_BUCKET_NAME=castleforever
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
S3_REGION_NAME=auto
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
S3_LOCATION=media
S3_QUERYSTRING_AUTH=0
```

Notes:

- Staging can keep `USE_S3_MEDIA=0` and use its `media_data` volume; production
  should use `USE_S3_MEDIA=1`.
- Production must use `DJANGO_DEBUG=0`. Staging may use `DJANGO_DEBUG=1` while
  it is access-restricted, in which case keep `DJANGO_SECURE_SSL_REDIRECT=0`
  and `DJANGO_HSTS_SECONDS=0` to avoid HTTPS redirects during debugging.
- `DATABASE_URL` must use `db` as the host inside Compose, and its user/password
  must match `POSTGRES_*`.
- Use separate buckets (or at least separate `S3_LOCATION` prefixes) for stage
  and prod.
- For a **private** bucket set `S3_QUERYSTRING_AUTH=1`. For a public/CDN bucket
  set it to `0` and point `S3_CUSTOM_DOMAIN` at the public hostname.
- Use a URL-safe `POSTGRES_PASSWORD` (letters/digits/`-`/`_`) to avoid escaping
  issues in `DATABASE_URL`.
- Quote values that contain `#` or `$`, e.g.
  `DJANGO_SECRET_KEY='...'`.

Generate secrets with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 3. Start an environment

The wrapper sets the Compose project name, env file and compose file for you:

```bash
# Staging
./deploy/compose.sh stage up -d --build

# Production
./deploy/compose.sh prod up -d --build
```

Equivalent direct commands (the wrapper adds `--project-name` for isolation):

```bash
docker compose --project-name castleforever-stage --env-file .env.stage up -d --build
docker compose --project-name castleforever-prod --env-file .env.prod up -d --build
```

The container entrypoint automatically:

1. applies database migrations;
2. runs `collectstatic`;
3. starts Gunicorn on port `8000` inside the container.

> Production validation is strict: with `USE_S3_MEDIA=1`, the app refuses to
> start until both `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY` are set and
> `S3_BUCKET_NAME` is present. Fill the secret in `.env.prod` before the first
> `prod` start.

First start:

```bash
./deploy/compose.sh prod ps
./deploy/compose.sh prod logs -f web
./deploy/compose.sh prod exec web python manage.py createsuperuser
```

Do **not** run `seed_catalog` in production unless you explicitly want the demo
catalog.

### Useful commands

```bash
./deploy/compose.sh prod ps
./deploy/compose.sh prod logs -f web
./deploy/compose.sh prod logs -f db
./deploy/compose.sh prod exec web python manage.py shell
./deploy/compose.sh prod exec web python /app/docker/healthcheck.py
./deploy/compose.sh prod restart web
```

Run `./deploy/compose.sh stage ...` for staging.

### Stop / remove

```bash
./deploy/compose.sh prod down          # keeps volumes and data
./deploy/compose.sh prod down -v       # DESTROYS database and media volumes
```

---

## 4. Host Nginx + HTTPS

Both containers bind to `127.0.0.1` only, so put a reverse proxy in front of
them. Copy the provided config and replace the domains if needed:

```bash
sudo cp deploy/nginx-docker.conf /etc/nginx/sites-available/castleforever-docker
sudo ln -s /etc/nginx/sites-available/castleforever-docker /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-available/castleforever-docker
sudo nginx -t
sudo systemctl reload nginx
```

Then issue certificates:

```bash
sudo certbot --nginx -d stage.castleforever.com
sudo certbot --nginx -d castleforever.com -d www.castleforever.com
```

`deploy/nginx-docker.conf` proxies everything to Gunicorn (WhiteNoise handles
static files) and forwards `X-Forwarded-Proto`, which Django uses for HTTPS
redirects and secure cookies.

If stage and prod are on different servers, remove the server block that does
not belong to that host. If you use Cloudflare or another load balancer for TLS,
you can skip Certbot and keep only the port-80 proxy block.

---

## 5. Deploying updates

```bash
cd /opt/castleforever
git pull --ff-only

./deploy/compose.sh prod up -d --build
# only if Dockerfile/requirements changed; otherwise `restart web` is enough

docker image prune -f
```

Migrations and `collectstatic` run automatically when the new `web` container
starts. For a code-only change:

```bash
./deploy/compose.sh prod up -d --build web
# or
./deploy/compose.sh prod restart web
```

Do the same with `stage` before promoting to production.

---

## 6. Backups

Database:

```bash
./deploy/compose.sh prod exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > "backup-$(date +%F).sql"
```

Restore:

```bash
./deploy/compose.sh prod stop web
cat backup-2026-11-14.sql | \
  ./deploy/compose.sh prod exec -T db \
  sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'
./deploy/compose.sh prod start web
```

Media in production lives in the bucket; enable versioning or lifecycle rules
there. In staging, back up the `media_data` volume if it contains anything you
care about.

List volumes:

```bash
docker volume ls | grep castleforever
```

---

## 7. Switching staging to the bucket

Staging is configured for local media (`USE_S3_MEDIA=0`). To use a bucket:

1. Create a separate stage bucket/prefix.
2. Fill in the `S3_*` values in `.env.stage` and set `USE_S3_MEDIA=1`.
3. Copy existing files out of the `media_data` volume:

```bash
./deploy/compose.sh stage exec -T web tar -C /app/media -cf - . \
  > stage-media.tar
```

4. Upload them to the bucket with `aws s3 sync`, `rclone` or the provider's UI,
   preserving paths such as `venues/...`.
5. Recreate the web container:

```bash
./deploy/compose.sh stage up -d --build web
```

For production, keep the same `S3_LOCATION=media` prefix so stored relative
paths continue to resolve.

---

## 8. Troubleshooting

| Symptom | Check |
| --- | --- |
| `POSTGRES_PASSWORD must be set` | The `--env-file` flag is missing, or `.env.stage` / `.env.prod` lacks the value. |
| `USE_S3_MEDIA=1 requires S3_BUCKET_NAME` | Fill `S3_BUCKET_NAME` in `.env.prod`. |
| `S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY must both be set` | Fill in the missing S3 credential. |
| `password authentication failed` | `POSTGRES_PASSWORD` and `DATABASE_URL` differ, or the existing `postgres_data` volume was initialized with a different password. |
| `502 Bad Gateway` from Nginx | `./deploy/compose.sh prod ps`, then `logs web`; confirm `APP_PORT` matches the Nginx upstream. |
| Uploads 403 from the bucket | Check the bucket policy/public access and `S3_QUERYSTRING_AUTH`; verify the API token can `PutObject`. |
| Images 404 | `S3_ENDPOINT_URL` must not include the bucket name; use the account endpoint only. |
| CSRF verification failed | Add the exact HTTPS origin to `CSRF_TRUSTED_ORIGINS`. |
| Static files 404 | Check `collectstatic` output in `logs web`; WhiteNoise needs `DJANGO_DEBUG=0` for manifest storage. |
| Container unhealthy | `./deploy/compose.sh prod logs web`; the probe calls `/healthz/` and fails if migrations or the database are broken. |
| Port already in use | Change `APP_PORT` in the env file and update the Nginx upstream. |

---

## 9. Security checklist

- [ ] `.env.stage` / `.env.prod` are not committed (`git check-ignore .env.prod`).
- [ ] Env files are `chmod 600` and owned by the deploy user.
- [ ] `DJANGO_SECRET_KEY` is unique per environment and long/random.
- [ ] Database passwords are unique per environment.
- [ ] Stage and prod use separate buckets or prefixes.
- [ ] Ports `8000` / `8001` are bound to `127.0.0.1` (as in `compose.yaml`).
- [ ] TLS is terminated by Nginx/Certbot (or a Cloudflare proxy).
- [ ] `DJANGO_DEBUG=0` in production (staging may use `1` only behind access restrictions).
- [ ] `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` contain the real domains.
- [ ] Regular `pg_dump` backups and bucket versioning are enabled.
