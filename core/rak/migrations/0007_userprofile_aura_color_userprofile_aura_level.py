# Generated by Django 5.1 on 2024-10-11 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rak', '0006_payitforward'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='aura_color',
            field=models.CharField(default='Blue', max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='aura_level',
            field=models.CharField(default='Beginner', max_length=255),
        ),
    ]