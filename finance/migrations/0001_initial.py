# Generated by Django 5.1.5 on 2025-03-03 06:35

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academic', '0007_alter_termexamsession_created_by_and_more'),
        ('students', '0004_alter_student_grade_of_entry'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherSchoolPayments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fees_type', models.CharField(choices=[('development', 'development'), ('sports', 'sports'), ('tuition', 'tuition'), ('library', 'library'), ('laboratory', 'laboratory'), ('uniform', 'uniform'), ('transport', 'transport'), ('hostel', 'hostel'), ('examination', 'examination'), ('medical', 'medical'), ('maintenance', 'maintenance'), ('technology', 'technology'), ('admission', 'admission'), ('field_trip', 'field_trip'), ('extra_classes', 'extra_classes')], max_length=150, unique=True)),
                ('amount', models.IntegerField()),
                ('description', models.TextField(default='No Description ...')),
                ('unique_code', models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.grade')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolFees',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tuitionfee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('hostelfee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('breakfastfee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('lunchfee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('description', models.TextField(default='No Description ...')),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('grade', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='school_fees', to='academic.grade')),
            ],
            options={
                'verbose_name_plural': 'SchoolFees',
            },
        ),
        migrations.CreateModel(
            name='StudentTuitionDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostel', models.BooleanField(default=False)),
                ('lunch', models.BooleanField(default=False)),
                ('breakfast', models.BooleanField(default=False)),
                ('total_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), editable=False, max_digits=10)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tuition_description', to='students.student')),
                ('tuition', models.ForeignKey(default=200000, on_delete=django.db.models.deletion.CASCADE, related_name='student_tuition_descriptions', to='finance.schoolfees')),
            ],
        ),
        migrations.CreateModel(
            name='FeeTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_due', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('card', 'Card'), ('online_transfer', 'Online Transfer'), ('mobile_money', 'Mobile Money')], max_length=20)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue')], default='pending', max_length=20)),
                ('last_payment_date', models.DateField(blank=True, null=True)),
                ('payment_reference', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('receipt_url', models.URLField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, help_text='Any additional notes about the payment', null=True)),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fee_transactions', to='finance.studenttuitiondescription')),
            ],
            options={
                'db_table': 'fee_transaction',
                'db_table_comment': "This includes students' fees transaction data",
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='TransportFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=150)),
                ('amount', models.IntegerField()),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
