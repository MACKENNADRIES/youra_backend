# Generated by Django 5.1 on 2024-10-21 07:32

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rak', '0012_remove_report_reported_user_remove_report_reporter_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='randomactofkindness',
            name='rak_claims',
            field=models.ManyToManyField(related_name='raks', to='rak.rakclaim'),
        ),
        migrations.AlterField(
            model_name='randomactofkindness',
            name='collaborators',
            field=models.ManyToManyField(blank=True, related_name='rak_collaborators', to=settings.AUTH_USER_MODEL),
        ),
    ]