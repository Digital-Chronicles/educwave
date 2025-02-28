# Generated by Django 5.1.4 on 2025-02-28 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTableComment(
            name='customuser',
            table_comment='Custom user model using email for authentication with role-based access',
        ),
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('TEACHER', 'Teacher'), ('FINANCE', 'Finance'), ('STUDENT', 'Student'), ('PARENT', 'Parent')], default='STUDENT', max_length=20),
        ),
    ]
