# Generated by Django 2.0 on 2018-06-04 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_profile_last_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_activity',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
