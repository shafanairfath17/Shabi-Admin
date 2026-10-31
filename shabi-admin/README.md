# Shabi Jewels: site + private admin

Django serves the public site (`site/`) and the admin. Products, prices, stock, images and collections live in the database; the public pages read them from `/api/`.

## Run locally
```
pip install -r requirements.txt
export DJANGO_DEBUG=1 DJANGO_SECRET_KEY=anything-local
python manage.py migrate
python manage.py createowner        # the ONE admin account (12+ char password)
python manage.py runserver
```
Site: http://127.0.0.1:8000/  Admin: http://127.0.0.1:8000/manage-shabi/ (change with `ADMIN_URL`).
Tests: `python manage.py test`

## Using the admin
- **Products**: add/edit, upload several photos (Image management = the photo section inside each product), set price, quantity, publish on/off. Quantity and "published" are editable straight from the list (stock management). Filter by collection / stock status / trash; search by name or SKU.
- **Stock rules**: 0 = Out of Stock, 1 to `LOW_STOCK_THRESHOLD` (default 3) = Low Stock, more = In Stock. Computed from quantity only.
- **Delete** moves a product to trash (filter "Deleted"; action "Restore").
- **Collections**: rename, cover image, order, enable/disable, add new ones (a new collection appears on the home page and opens `collection.html?c=slug`).
- **Settings**: Users, to change your password. Low-stock threshold = env var.

## Production (needs a host with a persistent disk; NOT Vercel)
Vercel cannot keep a database or uploaded photos. Use PythonAnywhere, Render (with a disk) or Railway (with a volume).
1. Set env vars from `.env.example` (`DJANGO_SECRET_KEY` long and random, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`).
2. `python manage.py collectstatic --noinput && python manage.py migrate && python manage.py createowner`
3. Serve with gunicorn (see `Procfile`) behind HTTPS.
4. Backups: regularly copy `db.sqlite3` and the `media/` folder (or `python manage.py dumpdata > backup.json`) to a safe place.

## Security built in
Hashed passwords, 8h sessions, secure cookies/HSTS/HTTPS redirect when `DEBUG=0`, CSRF, login lockout (5 failures = 30 min), single owner, public API is GET-only and returns published items only, uploads checked by real content and re-encoded to WebP with random names, CSP + nosniff headers. Not yet penetration-tested: run your own checks before relying on it.
