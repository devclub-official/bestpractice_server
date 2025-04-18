# Generated by Django 5.2 on 2025-04-18 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedconfig',
            name='bookmark_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='generatedconfig',
            name='is_bookmarked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='generatedconfig',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
