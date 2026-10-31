import logging
from django.contrib import admin, messages
from django.db.models import Count, Q
from django.conf import settings
from .models import Category, Product, ProductImage
log = logging.getLogger("shop.admin")
admin.site.site_header = "Shabi Jewels Admin"; admin.site.site_title = "Shabi Admin"; admin.site.index_title = "Dashboard"
admin.site.index_template = "admin/shabi_index.html"

class ImageInline(admin.TabularInline):
    model = ProductImage; extra = 1

class TrashFilter(admin.SimpleListFilter):
    title = "status"; parameter_name = "trash"
    def lookups(self, r, m): return [("1", "Deleted (trash)")]
    def queryset(self, r, qs): return qs.filter(deleted_at__isnull=False) if self.value() else qs.filter(deleted_at__isnull=True)

class StockFilter(admin.SimpleListFilter):
    title = "stock"; parameter_name = "stock"
    def lookups(self, r, m): return [("in", "In stock"), ("low", "Low stock"), ("out", "Out of stock")]
    def queryset(self, r, qs):
        return {"in": qs.filter(quantity__gt=settings.LOW_STOCK_THRESHOLD), "low": qs.filter(quantity__gt=0, quantity__lte=settings.LOW_STOCK_THRESHOLD), "out": qs.filter(quantity=0)}.get(self.value(), qs)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "quantity", "stock", "published", "updated")
    list_editable = ("quantity", "published"); list_per_page = 25
    list_filter = (TrashFilter, "category", StockFilter, "published"); search_fields = ("name", "sku")
    ordering = ("-updated",); inlines = [ImageInline]; actions = ["restore"]
    readonly_fields = ("created", "updated")
    @admin.display(description="Stock")
    def stock(self, o): return o.stock_label
    def get_queryset(self, r): return Product.all_objects.all()
    def delete_model(self, r, o): o.soft_delete(); log.info("product soft-deleted sku=%s by=%s", o.sku, r.user)
    def delete_queryset(self, r, qs):
        for o in qs: o.soft_delete()
        log.info("products soft-deleted count=%s by=%s", len(qs), r.user)
    def save_model(self, r, o, f, c):
        super().save_model(r, o, f, c); log.info("product saved sku=%s by=%s", o.sku, r.user)
        if o.stock_status == "out_of_stock": messages.error(r, f"{o.name} is now OUT OF STOCK.")
        elif o.stock_status == "low_stock": messages.warning(r, f"{o.name} is low on stock ({o.quantity} left). Time to restock.")
    @admin.action(description="Restore selected products from trash")
    def restore(self, r, qs): n = qs.update(deleted_at=None); messages.success(r, f"Restored {n} product(s).")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "enabled", "product_count"); list_editable = ("order", "enabled")
    prepopulated_fields = {"slug": ("name",)}
    def get_queryset(self, r): return super().get_queryset(r).annotate(n=Count("products", filter=Q(products__deleted_at__isnull=True)))
    @admin.display(description="Products", ordering="n")
    def product_count(self, o): return o.n

_index = admin.site.index
def index(request, extra_context=None):
    p = Product.objects.all()
    stats = [("Total products", p.count()), ("In stock", p.filter(quantity__gt=settings.LOW_STOCK_THRESHOLD).count()), ("Low stock", p.filter(quantity__gt=0, quantity__lte=settings.LOW_STOCK_THRESHOLD).count()),
             ("Out of stock", p.filter(quantity=0).count()), ("Collections", Category.objects.count())]
    return _index(request, {**(extra_context or {}), "stats": stats, "alerts": p.filter(quantity__lte=settings.LOW_STOCK_THRESHOLD).order_by("quantity"), "recent": p.order_by("-updated")[:5]})
admin.site.index = index
