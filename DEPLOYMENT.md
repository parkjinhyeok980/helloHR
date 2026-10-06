# Vercel deployment

JWT authentication requires `PyJWT==2.15.1` and migration
`accounts.0003_revokedtoken`. Install updated requirements, migrate, and restart
the backend. Tokens expire after 3,600 seconds. Active users renew valid tokens
through the CSRF-protected `/api/accounts/refresh/` endpoint, at most every
30 seconds; idle or hidden pages do not automatically renew tokens.
Configure `JWT_ACCESS_TTL_SECONDS` to change this lifetime and optionally set
`DJANGO_JWT_SIGNING_KEY` (defaults to `DJANGO_SECRET_KEY`). See [JWT authentication](docs/jwt-auth.md).

Guest login requires `accounts.0002_guest_account`. Run `python manage.py migrate`
before deploying: it creates the shared, non-staff `guest` account and transfers
unowned legacy trainings, employees, and departments to it while retaining
attendance and signature relationships. Data already owned by another account
is not transferred. Guest visitors share the same editable workspace.

After updating the signed attendance feature, run `python manage.py migrate`
against the deployment database before deploying the new application. Migration
`attendance.0002_signature_strokes` stores normalized handwritten strokes in the
database, so this feature does not depend on Vercel's temporary file storage.
Existing browser-only attendance demo records are not imported into the database.

Training QR images encode the current site's origin and `?training=<id>`.
Generate shared QR images on the deployed site; localhost QR links only work on
the computer hosting the development server. QR rendering uses the browser API
documented by [node-qrcode](https://github.com/soldair/node-qrcode#browser).

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

After signing up in the application, optionally run
`python manage.py seed_demo --email manager@example.com` to add sample trainings
and participants to that account.

The account feature adds `accounts.0001_initial`, `employees.0002`, and
`trainings.0003`. Apply all migrations before deploying this version. Existing
unowned data is preserved but hidden from account dashboards. To assign it to an
explicitly chosen registered account, preview with
`python manage.py assign_legacy_data --email manager@example.com`, then add
`--apply` to perform the transfer. See [the account ERD and migration guide](docs/account-erd.md).

Check `/api/csrf/` after deployment. It should return JSON. The application
uses local file storage for uploads; persistent uploads require an external
object store before those features can be used reliably on Vercel.
