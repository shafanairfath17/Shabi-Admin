import io
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from .models import Category, Product, ProductImage

def png(n="a.png", size=(40, 40)):
    b = io.BytesIO(); Image.new("RGB", size, "gold").save(b, "PNG"); return SimpleUploadedFile(n, b.getvalue(), "image/png")

class Base(TestCase):
    def setUp(self):
        self.cat = Category.objects.get(slug="rings")
        self.p = Product.objects.create(category=self.cat, name="Floral Ring", sku="R1", price=199, quantity=8)

class PublicApi(Base):
    def test_published_only_and_stock_fields(self):
        Product.objects.create(category=self.cat, name="Hidden", sku="R2", quantity=5, published=False)
        d = self.client.get("/api/collections/rings/").json()["products"]
        self.assertEqual([x["sku"] for x in d], ["R1"]); self.assertEqual(d[0]["price"], 199.0)
        self.assertEqual(d[0]["quantity"], 8); self.assertEqual(d[0]["stock"], "in_stock")
    def test_stock_states_and_labels(self):
        for q, s in ((8, "in_stock"), (3, "low_stock"), (0, "out_of_stock")):
            self.p.quantity = q; self.p.save(); self.assertEqual(self.p.stock_status, s)
        self.assertEqual(self.p.stock_label, "Out of Stock")
    def test_soft_deleted_and_disabled_hidden(self):
        self.p.soft_delete(); self.assertEqual(self.client.get("/api/collections/rings/").json()["products"], [])
        Category.objects.filter(slug="rings").update(enabled=False)
        self.assertEqual(self.client.get("/api/collections/rings/").status_code, 404)
    def test_necklaces_seeded_and_read_only(self):
        self.assertEqual([c["slug"] for c in self.client.get("/api/categories/").json()["categories"]], ["rings", "bracelets", "necklaces"])
        self.assertEqual(self.client.post("/api/collections/rings/").status_code, 405)

class Uploads(Base):
    def test_valid_image_is_reencoded_webp_random_name(self):
        i = ProductImage.objects.create(product=self.p, image=png("../../evil.png")); self.assertTrue(i.image.name.endswith(".webp")); self.assertNotIn("evil", i.image.name); i.image.delete()
    def test_non_image_rejected(self):
        from django.core.exceptions import ValidationError
        from .models import validate_image
        with self.assertRaises(ValidationError): validate_image(SimpleUploadedFile("x.png", b"<?php echo 1;", "image/png"))

class AdminSecurity(Base):
    url = "/manage-shabi/"
    def test_anonymous_redirected(self):
        for u in (self.url, self.url + "shop/product/", self.url + "shop/product/add/"): self.assertEqual(self.client.get(u).status_code, 302)
    def test_owner_crud_and_dashboard(self):
        self.client.force_login(get_user_model().objects.create_superuser("owner", password="a-long-strong-pass-1"))
        self.assertContains(self.client.get(self.url), "Total products")
        r = self.client.post(self.url + "shop/product/add/", {"category": self.cat.pk, "name": "N", "sku": "N1", "price": "99", "quantity": "2", "published": "on", "images-TOTAL_FORMS": 0, "images-INITIAL_FORMS": 0})
        self.assertEqual(r.status_code, 302); self.assertEqual(Product.objects.get(sku="N1").stock_status, "low_stock")
        self.client.post(self.url + "shop/product/%d/delete/" % self.p.pk, {"post": "yes"}); self.assertFalse(Product.objects.filter(pk=self.p.pk).exists()); self.assertTrue(Product.all_objects.filter(pk=self.p.pk).exists())
    def test_login_lockout_after_failures(self):
        get_user_model().objects.create_superuser("owner", password="a-long-strong-pass-1")
        for _ in range(5): self.client.post(self.url + "login/", {"username": "owner", "password": "wrong"})
        r = self.client.post(self.url + "login/", {"username": "owner", "password": "a-long-strong-pass-1"}); self.assertEqual(r.status_code, 429)
    def test_single_owner_only(self):
        with override_settings():
            import os; os.environ["OWNER_USERNAME"] = "owner"; os.environ["OWNER_PASSWORD"] = "a-long-strong-pass-1"
            call_command("createowner")
            with self.assertRaises(CommandError): call_command("createowner")
