from django.db import migrations


def remove_invalid_permission(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Permission.objects.filter(codename="can_validate_ordrew", content_type__app_label="conventionnement").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("conventionnement", "0007_update_ordretravail_permissions"),
    ]

    operations = [
        migrations.RunPython(remove_invalid_permission, migrations.RunPython.noop),
    ]
