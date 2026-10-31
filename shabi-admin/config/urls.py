from django.conf import settings
from django.contrib import admin
from django.http import Http404
from django.urls import path, re_path
from django.views.static import serve
from shop import views
urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/categories/", views.categories),
    path("api/collections/<slug:slug>/", views.collection),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]


def site(request, path=""):
    """Serve the public website files (index.html, rings.html, css, js, images)."""
    path = path or "index.html"
    try: return serve(request, path, document_root=settings.SITE_DIR)
    except Http404: raise
urlpatterns.append(re_path(r"^(?P<path>.*)$", site))
