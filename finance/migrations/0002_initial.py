# Generated by Django 5.1.4 on 2025-02-13 21:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('finance', '0001_initial'),
        ('students', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='studenttuitiondescription',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tuition_description', to='students.student'),
        ),
        migrations.AddField(
            model_name='studenttuitiondescription',
            name='tuition',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_tuition_descriptions', to='finance.schoolfees'),
        ),
        migrations.AddField(
            model_name='feetransaction',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fee_transactions', to='finance.studenttuitiondescription'),
        ),
        migrations.AddField(
            model_name='transportfee',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
