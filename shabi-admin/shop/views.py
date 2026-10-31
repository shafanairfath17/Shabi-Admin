from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from .models import Category, Product

def _img(f): return f.url if f else ""
def _list(s): return [x.strip() for x in s.split(",") if x.strip()]

@require_GET
def categories(request):
    data = [{"slug": c.slug, "name": c.name, "description": c.description, "cover": _img(c.cover), "url": c.url}
            for c in Category.objects.filter(enabled=True)]
    return JsonResponse({"categories": data})

@require_GET
def collection(request, slug):
    try: c = Category.objects.get(slug=slug, enabled=True)
    except Category.DoesNotExist: raise Http404
    items = Product.objects.filter(category=c, published=True).prefetch_related("images")
    out = []
    for p in items:
        imgs = [{"url": i.image.url, "alt": i.alt or p.name} for i in p.images.all()]
        out.append({"sku": p.sku, "name": p.name, "desc": p.description, "price": float(p.price) if p.price is not None else None,
                    "img": imgs[0]["url"] if imgs else "", "images": imgs, "material": p.material, "colors": _list(p.colors),
                    "sizes": _list(p.sizes), "care": p.care, "stock": p.stock_status, "quantity": p.quantity, "label": p.stock_label})
    r = JsonResponse({"category": {"name": c.name, "description": c.description}, "products": out})
    r["Cache-Control"] = "public, max-age=30"; return r
