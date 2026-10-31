from django.db import migrations
def seed(apps, se):
    C = apps.get_model("shop", "Category")
    for i, n in enumerate(["Rings", "Bracelets", "Necklaces"], 1):
        C.objects.get_or_create(slug=n.lower(), defaults={"name": n, "order": i})
class Migration(migrations.Migration):
    dependencies = [("shop", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
