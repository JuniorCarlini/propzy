# Generated migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("landings", "0003_alter_landingpage_theme_alter_property_landing_page_and_more"),
        ("properties", "0002_rename_landing_page_to_site"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="LandingPage",
            new_name="Site",
        ),
        migrations.AlterModelTable(
            name="site",
            table="landings_landingpage",  # Mantém o nome da tabela no banco
        ),
    ]
