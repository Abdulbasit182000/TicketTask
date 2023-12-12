# Generated by Django 4.2.7 on 2023-12-11 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_profile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(blank=True, choices=[('MA', 'Manager'), ('QA', 'QA'), ('DEV', 'Developer')], default='DEV', max_length=3),
        ),
    ]