import uuid
from io import BytesIO
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = 25_000_000
MAX_BYTES = 5 * 1024 * 1024

def validate_image(f):
    """Checks real file content (not the extension) and size."""
    if f.size > MAX_BYTES: raise ValidationError("Image must be 5 MB or smaller.")
    try:
        im = Image.open(f); fmt = im.format; im.verify(); f.seek(0)
    except Exception:
        raise ValidationError("Upload a valid JPEG, PNG or WebP image.")
    if fmt not in ("JPEG", "PNG", "WEBP"): raise ValidationError("Only JPEG, PNG or WebP images are allowed.")

def reencode(field_file):
    """Re-encode to WebP with a random name: strips metadata/payloads, caps size."""
    if not field_file or getattr(field_file, "_committed", True): return
    im = ImageOps.exif_transpose(Image.open(field_file)); im.thumbnail((1600, 1600))
    im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    buf = BytesIO(); im.save(buf, "WEBP", quality=82)
    field_file.save(f"{uuid.uuid4().hex}.webp", ContentFile(buf.getvalue()), save=False)

class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=200, blank=True)
    cover = models.ImageField(upload_to="categories/", blank=True, validators=[validate_image])
    order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    class Meta: ordering = ["order", "name"]; verbose_name_plural = "collections"
    def __str__(self): return self.name
    @property
    def url(self): return f"{self.slug}.html" if self.slug in ("rings", "bracelets", "necklaces") else f"collection.html?c={self.slug}"
    def save(self, *a, **k):
        self.slug = self.slug or slugify(self.name); reencode(self.cover); super().save(*a, **k)

class ActiveManager(models.Manager):
    def get_queryset(self): return super().get_queryset().filter(deleted_at__isnull=True)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=120)
    sku = models.CharField("SKU", max_length=40, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, help_text="Leave empty to show 'DM for price'.")
    quantity = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)
    material = models.CharField(max_length=120, blank=True, default="Stainless steel, anti-tarnish")
    colors = models.CharField(max_length=120, blank=True, help_text="Comma separated, e.g. Gold, Silver")
    sizes = models.CharField(max_length=120, blank=True, help_text="Comma separated, e.g. 6, 7, 8")
    care = models.CharField(max_length=200, blank=True, default="Wipe dry after use and store in a pouch. Avoid harsh perfumes.")
    created = models.DateTimeField(auto_now_add=True); updated = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)  # soft delete
    objects = ActiveManager(); all_objects = models.Manager()
    def __str__(self): return f"{self.name} ({self.sku})"
    @property
    def stock_status(self):
        return "out_of_stock" if self.quantity <= 0 else "low_stock" if self.quantity <= settings.LOW_STOCK_THRESHOLD else "in_stock"
    @property
    def stock_label(self):
        q = self.quantity; unit = "piece" if q == 1 else "pieces"
        return {"out_of_stock": "Out of Stock", "low_stock": f"Low Stock: only {q} {unit} left", "in_stock": f"In Stock: {q} {unit} left"}[self.stock_status]
    def soft_delete(self): self.deleted_at = timezone.now(); self.save(update_fields=["deleted_at", "updated"])

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", validators=[validate_image])
    alt = models.CharField(max_length=140, blank=True)
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["order", "id"]
    def save(self, *a, **k): reencode(self.image); super().save(*a, **k)
