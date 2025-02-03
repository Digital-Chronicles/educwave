# Generated by Django 5.1.4 on 2025-01-30 12:16

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('management', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_id', models.CharField(max_length=100, unique=True)),
                ('nin_number', models.CharField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('gender', models.CharField(choices=[('male', 'male'), ('female', 'female')], default='male', max_length=50)),
                ('year_of_entry', models.CharField(max_length=4, validators=[django.core.validators.RegexValidator(message='Year must be in YYYY format.', regex='^\\d{4}$')], verbose_name='Year of Entry')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='teacher_profile_pictures')),
                ('registered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='registered_teachers', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='management.generalinformation')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='teacher', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'teachers',
            },
        ),
        migrations.CreateModel(
            name='PayrollInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bank_name', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=50, unique=True)),
                ('tax_identification_number', models.CharField(max_length=50, unique=True)),
                ('nssf_number', models.CharField(max_length=50, unique=True)),
                ('payment_frequency', models.CharField(choices=[('monthly', 'Monthly'), ('bi-weekly', 'Bi-Weekly'), ('weekly', 'Weekly')], max_length=20)),
                ('teacher', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payroll_information', to='teachers.teacher')),
            ],
            options={
                'db_table': 'payroll_information',
            },
        ),
        migrations.CreateModel(
            name='NextOfKin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('relationship', models.CharField(max_length=50)),
                ('contact_number', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('teacher', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='next_of_kin', to='teachers.teacher')),
            ],
            options={
                'db_table': 'next_of_kin',
            },
        ),
        migrations.CreateModel(
            name='EmploymentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('responsibilities', models.TextField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employment_history', to='teachers.teacher')),
            ],
            options={
                'db_table': 'employment_history',
            },
        ),
        migrations.CreateModel(
            name='EducationBackground',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('education_award', models.CharField(max_length=100)),
                ('institution', models.CharField(max_length=100)),
                ('graduation_year', models.IntegerField()),
                ('result_obtained', models.CharField(max_length=10)),
                ('additional_certifications', models.TextField(blank=True, null=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education_background', to='teachers.teacher')),
            ],
            options={
                'db_table': 'education_background',
            },
        ),
        migrations.CreateModel(
            name='CurrentEmployment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=100)),
                ('department', models.CharField(max_length=100)),
                ('teacher', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='current_employment', to='teachers.teacher')),
            ],
            options={
                'db_table': 'current_employment',
            },
        ),
    ]
