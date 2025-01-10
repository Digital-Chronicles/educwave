# Generated by Django 5.1.4 on 2025-01-10 09:12

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academic', '0001_initial'),
        ('management', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_id', models.CharField(editable=False, max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('date_of_birth', models.DateField()),
                ('current_status', models.CharField(choices=[('active', 'Active'), ('graduated', 'Graduated'), ('dropped out', 'Dropped Out')], max_length=50)),
                ('year_of_entry', models.CharField(max_length=4, validators=[django.core.validators.RegexValidator(message='Year must be in YYYY format.', regex='^\\d{4}$')], verbose_name='Year of Entry')),
                ('guardian_name', models.CharField(blank=True, max_length=150, null=True)),
                ('guardian_phone', models.CharField(blank=True, max_length=150, null=True)),
                ('father_name', models.CharField(blank=True, max_length=150, null=True)),
                ('father_phone', models.CharField(blank=True, max_length=150, null=True)),
                ('mother_name', models.CharField(blank=True, max_length=150, null=True)),
                ('mother_phone', models.CharField(blank=True, max_length=150, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='')),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('current_grade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academic.grade')),
                ('registered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='management.generalinformation')),
            ],
            options={
                'db_table': 'students',
                'db_table_comment': 'This includes Students data',
                'ordering': ['first_name'],
            },
        ),
        migrations.CreateModel(
            name='CareTaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('relationship', models.CharField(max_length=50)),
                ('contact_number', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student')),
            ],
            options={
                'db_table': 'caretaker',
                'db_table_comment': 'This includes Students care taker data',
                'order_with_respect_to': 'student',
            },
        ),
        migrations.CreateModel(
            name='StudentAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=20)),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='students.student')),
            ],
            options={
                'db_table': 'students_address',
                'db_table_comment': 'This includes Students address data',
                'order_with_respect_to': 'student',
            },
        ),
        migrations.CreateModel(
            name='StudentGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_date', models.DateField()),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.grade')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='students.student')),
            ],
            options={
                'db_table': 'students_class',
                'db_table_comment': 'This includes Students class data',
                'order_with_respect_to': 'student',
            },
        ),
    ]
