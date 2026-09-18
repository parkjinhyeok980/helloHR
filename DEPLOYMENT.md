# Vercel deployment

Set the Vercel project's Root Directory to the repository root. The root
`vercel.json` builds the Vue app from `FE/` and routes `/api/*` to the Django
function in `api/index.py`.

Set these environment variables in Vercel before deploying:

- `DATABASE_URL`: a persistent PostgreSQL connection string. The local SQLite
  database is ignored by Git and Vercel functions do not provide persistent
  writable storage.
- `DJANGO_SECRET_KEY`: a unique production secret.
- `DJANGO_ALLOWED_HOSTS`: comma-separated custom domains, if used. Vercel
  preview and production `*.vercel.app` domains are already allowed.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated `https://` custom origins,
  if used.

Run Django migrations against the production database before using the API:

```powershell
$env:DJANGO_SECRET_KEY = '<same secret configured in Vercel>'
$env:DATABASE_URL = '<production PostgreSQL URL>'
pip install -r requirements.txt
cd BE
python manage.py migrate
```

Check `/api/csrf/` after deployment. It should return JSON. The application
uses local file storage for uploads; persistent uploads require an external
object store before those features can be used reliably on Vercel.
