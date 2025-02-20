# Generated by Django 5.1.4 on 2025-02-19 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0003_alter_studentmark_options_and_more'),
        ('students', '0004_alter_student_grade_of_entry'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentmark',
            options={'ordering': ['-term__year', 'term__term_name', 'student__registration_id']},
        ),
        migrations.AlterModelOptions(
            name='termexamsession',
            options={'ordering': ['-year', 'term_name']},
        ),
        migrations.AlterModelTableComment(
            name='studentmark',
            table_comment=None,
        ),
        migrations.AlterModelTableComment(
            name='termexamsession',
            table_comment=None,
        ),
        migrations.RemoveConstraint(
            model_name='studentmark',
            name='unique_student_subject_term',
        ),
        migrations.RemoveIndex(
            model_name='studentmark',
            name='student_mar_student_d10459_idx',
        ),
        migrations.RemoveIndex(
            model_name='studentmark',
            name='student_mar_term_id_dbf08f_idx',
        ),
        migrations.AlterField(
            model_name='termexamsession',
            name='term_name',
            field=models.CharField(choices=[('term_1', 'Term 1'), ('term_2', 'Term 2'), ('term_3', 'Term 3')], max_length=10, verbose_name='Term Name'),
        ),
        migrations.AlterField(
            model_name='termexamsession',
            name='year',
            field=models.PositiveIntegerField(default=2025, verbose_name='Academic Year'),
        ),
        migrations.AlterUniqueTogether(
            name='studentmark',
            unique_together={('student', 'subject', 'term')},
        ),
    ]
