from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0005_alter_venue_country"),
        # Existing core migrations still reference ``catalog.venue``; apply them
        # before renaming the model so fresh databases can migrate cleanly.
        ("core", "0007_alter_servicerequest_destination_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Venue",
            new_name="Estate",
        ),
        migrations.RenameModel(
            old_name="VenueImage",
            new_name="EstateImage",
        ),
        migrations.RenameField(
            model_name="estateimage",
            old_name="venue",
            new_name="estate",
        ),
        migrations.AlterField(
            model_name="estate",
            name="cover_image",
            field=models.ImageField(
                blank=True,
                help_text="Optional uploaded cover image",
                upload_to="estates/",
            ),
        ),
        migrations.AlterField(
            model_name="estateimage",
            name="image",
            field=models.ImageField(blank=True, upload_to="estates/"),
        ),
    ]
