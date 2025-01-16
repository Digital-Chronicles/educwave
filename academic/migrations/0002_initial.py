# Generated by Django 5.1.4 on 2025-01-13 08:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academic', '0001_initial'),
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='created_by',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='exams', to='teachers.teacher'),
        ),
        migrations.AddField(
            model_name='grade',
            name='class_teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grades', to='teachers.teacher'),
        ),
        migrations.AddField(
            model_name='exam',
            name='grade',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='exams', to='academic.grade'),
        ),
        migrations.AddField(
            model_name='notes',
            name='created_by',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='exam', to='teachers.teacher'),
        ),
        migrations.AddField(
            model_name='notes',
            name='grade',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='exam', to='academic.grade'),
        ),
        migrations.AddField(
            model_name='subject',
            name='curriculum',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='academic.curriculum'),
        ),
        migrations.AddField(
            model_name='notes',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='academic.subject'),
        ),
        migrations.AddField(
            model_name='exam',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='academic.subject'),
        ),
        migrations.AddField(
            model_name='topic',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='academic.subject'),
        ),
        migrations.AddField(
            model_name='notes',
            name='topics',
            field=models.ManyToManyField(related_name='notes', to='academic.topic'),
        ),
        migrations.AlterOrderWithRespectTo(
            name='notes',
            order_with_respect_to='subject',
        ),
        migrations.AlterOrderWithRespectTo(
            name='exam',
            order_with_respect_to='subject',
        ),
    ]
