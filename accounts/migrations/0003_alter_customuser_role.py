# Generated by Django 5.1.4 on 2025-02-28 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_table_comment_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('ACADEMIC', 'Academic'), ('TEACHER', 'Teacher'), ('FINANCE', 'Finance'), ('STUDENT', 'Student'), ('PARENT', 'Parent')], default='STUDENT', max_length=20),
        ),
    ]
