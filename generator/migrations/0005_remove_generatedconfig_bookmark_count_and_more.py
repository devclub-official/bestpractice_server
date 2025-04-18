# Generated by Django 5.2 on 2025-04-18 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0004_rename_fine_name_generatedconfig_finename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generatedconfig',
            name='bookmark_count',
        ),
        migrations.RemoveField(
            model_name='generatedconfig',
            name='features',
        ),
        migrations.RemoveField(
            model_name='generatedconfig',
            name='finename',
        ),
        migrations.AddField(
            model_name='generatedconfig',
            name='filename',
            field=models.CharField(blank=True, help_text='파일명', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='generatedconfig',
            name='selected_options',
            field=models.JSONField(default=dict, help_text='사용자가 선택한 옵션 및 설정값'),
        ),
        migrations.AlterField(
            model_name='generatedconfig',
            name='content',
            field=models.TextField(help_text='생성된 설정 파일 내용'),
        ),
        migrations.AlterField(
            model_name='generatedconfig',
            name='file_format',
            field=models.CharField(blank=True, help_text='파일 형식 (예: json, yaml)', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='generatedconfig',
            name='framework',
            field=models.CharField(help_text='프레임워크 (예: react, django)', max_length=50),
        ),
        migrations.AlterField(
            model_name='generatedconfig',
            name='language',
            field=models.CharField(help_text='프로그래밍 언어 (예: javascript, python)', max_length=50),
        ),
        migrations.AlterField(
            model_name='generatedconfig',
            name='mime_type',
            field=models.CharField(blank=True, help_text='MIME 타입', max_length=50, null=True),
        ),
    ]
