# Generated manually for the public Mission command page.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('uploads', '0002_mission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='assignee_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
