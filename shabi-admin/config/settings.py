import os
from pathlib import Path
from datetime import timedelta
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get("DJANGO_DEBUG") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or ("dev-only-insecure-key" if DEBUG else None)
if not SECRET_KEY: raise RuntimeError("Set DJANGO_SECRET_KEY")
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver,.vercel.app").split(",")]
CSRF_TRUSTED_ORIGINS = ["https://*" + h if h.startswith(".") else "https://" + h for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1", "testserver")]
ADMIN_URL = os.environ.get("ADMIN_URL", "manage-shabi/")
INSTALLED_APPS = ["django.contrib.admin","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","axes","shop"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware","whitenoise.middleware.WhiteNoiseMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware","shop.middleware.csp","axes.middleware.AxesMiddleware"]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {"default":{"ENGINE":"django.db.backends.sqlite3","NAME":os.environ.get("DB_PATH", BASE_DIR/"db.sqlite3")}}
if os.environ.get("DATABASE_URL"):   # Neon / any Postgres (set in Vercel)
    import urllib.parse as _u
    _p = _u.urlparse(os.environ["DATABASE_URL"])
    DATABASES["default"] = {"ENGINE":"django.db.backends.postgresql","NAME":_p.path.lstrip("/"),"USER":_u.unquote(_p.username or ""),"PASSWORD":_u.unquote(_p.password or ""),"HOST":_p.hostname,"PORT":_p.port or 5432,"OPTIONS":{"sslmode":"require"},"CONN_MAX_AGE":0}
AUTH_PASSWORD_VALIDATORS = [{"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator","OPTIONS":{"min_length":12}},{"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},{"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"}]
AUTHENTICATION_BACKENDS = ["axes.backends.AxesStandaloneBackend","django.contrib.auth.backends.ModelBackend"]
AXES_FAILURE_LIMIT = 5; AXES_COOLOFF_TIME = timedelta(minutes=30); AXES_LOCKOUT_PARAMETERS = ["ip_address"]
AXES_IPWARE_META_PRECEDENCE_ORDER = ["HTTP_X_FORWARDED_FOR", "REMOTE_ADDR"]  # real visitor IP behind Vercel
STATIC_URL = "/static/"; STATIC_ROOT = BASE_DIR/"staticfiles"
STORAGES = {"default":{"BACKEND":"django.core.files.storage.FileSystemStorage"},"staticfiles":{"BACKEND":"whitenoise.storage.CompressedStaticFilesStorage"}}
SITE_DIR = BASE_DIR/"site"
MEDIA_URL = "/media/"; MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR/"media"))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_COOKIE_HTTPONLY = True; SESSION_COOKIE_AGE = 60*60*8; SESSION_COOKIE_SAMESITE = "Lax"
DATA_UPLOAD_MAX_MEMORY_SIZE = 12*1024*1024
if not DEBUG:
    SECURE_SSL_REDIRECT = True; SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO","https")
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000; SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

LOW_STOCK_THRESHOLD = int(os.environ.get("LOW_STOCK_THRESHOLD", "3"))

if os.environ.get("CLOUDINARY_URL"):   # product photos live in Cloudinary, not on the server disk
    STORAGES["default"] = {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}
