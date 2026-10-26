from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("conventionnement", "0006_alter_ordretravail_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ordretravail",
            options={
                "permissions": [
                    ("can_validate_ordretravail", "Peut valider ou refuser un ordre de travail"),
                    ("can_realize_intervention", "Peut réaliser une intervention"),
                    ("can_create_ordretravail", "Peut créer un ordre de travail"),
                    ("can_create_bonlivraison", "Peut créer un bon de livraison"),
                    ("can_create_facture", "Peut créer une facture"),
                    ("can_unlock_ordretravail", "Peut déverrouiller un ordre de travail"),
                ],
            },
        ),
    ]
