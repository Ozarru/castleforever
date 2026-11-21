import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0006_rename_estate"),
        ("core", "0007_alter_servicerequest_destination_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="booking",
            old_name="venue",
            new_name="estate",
        ),
        migrations.RenameField(
            model_name="booking",
            old_name="quoted_venue_total",
            new_name="quoted_estate_total",
        ),
        migrations.RenameField(
            model_name="testimonial",
            old_name="venue",
            new_name="estate",
        ),
        migrations.RenameField(
            model_name="weddingrecord",
            old_name="venue",
            new_name="estate",
        ),
        migrations.RenameField(
            model_name="appointment",
            old_name="venue",
            new_name="estate",
        ),
        migrations.AlterField(
            model_name="appointment",
            name="estate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="appointments",
                to="catalog.estate",
                verbose_name="Estate of interest",
            ),
        ),
        migrations.AlterField(
            model_name="booking",
            name="estate",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bookings",
                to="catalog.estate",
            ),
        ),
        migrations.AlterField(
            model_name="testimonial",
            name="estate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="testimonials",
                to="catalog.estate",
                verbose_name="Estate",
            ),
        ),
        migrations.AlterField(
            model_name="weddingrecord",
            name="estate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="wedding_records",
                to="catalog.estate",
                verbose_name="Estate",
            ),
        ),
    ]
