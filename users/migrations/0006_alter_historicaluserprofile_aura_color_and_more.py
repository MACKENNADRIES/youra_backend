# Generated by Django 5.1 on 2024-12-08 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_historicaluserprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='aura_color',
            field=models.CharField(default='#50C878', max_length=50),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='aura_color',
            field=models.CharField(default='#50C878', max_length=50),
        ),
    ]