import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_notification_read"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="WeddingRecord",
            new_name="EventRecord",
        ),
        migrations.RenameField(
            model_name="eventrecord",
            old_name="wedding_date",
            new_name="event_date",
        ),
        migrations.RenameField(
            model_name="eventrecord",
            old_name="couple_names",
            new_name="client_names",
        ),
        migrations.AddField(
            model_name="eventrecord",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("wedding", "Wedding"),
                    ("engagement", "Engagement"),
                    ("anniversary", "Anniversary"),
                    ("corporate", "Corporate event"),
                    ("other", "Other"),
                ],
                default="wedding",
                max_length=20,
                verbose_name="Event type",
            ),
        ),
        migrations.AlterField(
            model_name="eventrecord",
            name="estate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="event_records",
                to="catalog.estate",
                verbose_name="Estate",
            ),
        ),
        migrations.AlterField(
            model_name="eventrecord",
            name="event_date",
            field=models.DateField(verbose_name="Event date"),
        ),
        migrations.AlterField(
            model_name="eventrecord",
            name="client_names",
            field=models.CharField(blank=True, max_length=180, verbose_name="Client names"),
        ),
        migrations.AlterModelOptions(
            name="eventrecord",
            options={
                "ordering": ["-event_date"],
                "verbose_name": "Event record",
                "verbose_name_plural": "Event records",
            },
        ),
    ]
