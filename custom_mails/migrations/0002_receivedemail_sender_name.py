# Generated by Django 5.0.6 on 2024-07-22 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_mails', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='receivedemail',
            name='sender_name',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
