# LanguageApp-IdentitySvc

Identity microservice for LanguageApp, built with FastAPI and SQLAlchemy.

## CI/CD and Docker

Docker images are built and pushed to **Docker Hub** by GitHub Actions when you push a **tag**. The environment (Prod vs Test) is determined by **which branch contains the tag’s commit**:

- **Tag’s commit on `main`** → **Prod** image is built and pushed (image tag + `latest`).
- **Tag’s commit on `test`** → **Test** image is built and pushed (image tag only).
- If the commit is on both branches, **Prod** is used (main takes precedence). If on neither, the workflow is skipped.

### GitHub secrets (required)

In the repo **Settings → Secrets and variables → Actions**, add:

- **`DOCKERHUB_USERNAME`** – your Docker Hub username.
- **`DOCKERHUB_TOKEN`** – a Docker Hub access token (Account → Security → New Access Token, Read & Write).

### Docker Hub and workflow config

- Create a repository on Docker Hub (e.g. `languageapp-identity`). The workflow uses the repo name set in [.github/workflows/build-and-push-docker.yml](.github/workflows/build-and-push-docker.yml) (`DOCKER_IMAGE_REPO`); change it if your repo name differs.
- After a tag push, the image is available as `$DOCKERHUB_USERNAME/$DOCKER_IMAGE_REPO:<tag>` (and `:latest` for Prod).

### Azure Web Apps

- **Prod:** Use image `youruser/languageapp-identity:latest` or a specific tag (e.g. `:v1.0.0`).
- **Test:** Use image `youruser/languageapp-identity:<test-tag>` (e.g. a tag pushed from the `test` branch).

See **Azure Web App** below for required app settings and port.

## Documentation
- For database drivers, connection strings, async runtime details, and environment variables see [databases/README.md](databases/README.md).

## Azure Web App

To run this service on Azure Web App for Containers using the Docker image:

1. **Port**: The container **listens on port 80 by default**, which matches Azure's default. Do **not** set `WEBSITES_PORT` unless you need a different port. If you previously had `WEBSITES_PORT=8000`, **remove it** so the app uses port 80 and Azure can reach it.

2. **Required application settings** (all must be set in Azure; no `.env` is copied into the image):
   - `IDENTITY_DATABASE_URL` – Async connection string (e.g. `mssql+aioodbc://...?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&...`)
   - `IDENTITY_DATABASE_MIGRATION_URL` – Same format, for Alembic migrations
   - If you use Azure **Connection strings** instead of Application settings, name them exactly **`IDENTITY_DATABASE_URL`** and **`IDENTITY_DATABASE_MIGRATION_URL`** (or `IdentityDatabaseUrl` / `IdentityDatabaseMigrationUrl`). The app reads both the standard names and Azure’s prefixed names (`SQLCONNSTR_*`, `SQLAZURECONNSTR_*`, `CUSTOMCONNSTR_*`).
   - `SECRET_TOKEN_KEY` – JWT secret (min 32 chars)
   - `AUTH_ALGORITHM` – e.g. `HS256`
   - `TOKEN_TIME_DELTA_IN_MINUTES` – Integer > 0
   - `DEFAULT_USER_ROLE` – e.g. `User`
   - `TOKEN_URL` – e.g. `/token`
   - `SERVICE_ID` – UUID for this service (RBAC/tracing)

3. **Optional for Azure**: `LOKI_ENABLED=false`, `METRICS_ENABLED=false`, `TRACING_ENABLED=false` (Tempo/Loki/Prometheus are disabled by default), `CORS_ALLOW_ORIGINS`, `LOG_LEVEL`.

4. **Health check**: In Configuration → General settings, set **Health check path** to `/health`.

5. **After deploy**: Open the main site (e.g. `https://your-identity-service.azurewebsites.net`). You should get `/`, `/docs`, and `/health`. Do not use the SCM URL (`https://your-identity-service.scm.azurewebsites.net`).