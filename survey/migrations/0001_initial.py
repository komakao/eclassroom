# Generated by Django 2.1.2 on 2019-05-21 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PostSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField(default=0)),
                ('fill_time', models.DateTimeField(auto_now_add=True)),
                ('p1', models.IntegerField(default=0)),
                ('p2', models.IntegerField(default=0)),
                ('p3', models.IntegerField(default=0)),
                ('p4', models.IntegerField(default=0)),
                ('p5', models.IntegerField(default=0)),
                ('p6', models.IntegerField(default=0)),
                ('p7', models.IntegerField(default=0)),
                ('p8', models.IntegerField(default=0)),
                ('p9', models.IntegerField(default=0)),
                ('p10', models.IntegerField(default=0)),
                ('p11', models.IntegerField(default=0)),
                ('p12', models.IntegerField(default=0)),
                ('p13', models.IntegerField(default=0)),
                ('p14', models.IntegerField(default=0)),
                ('p15', models.IntegerField(default=0)),
                ('p16', models.IntegerField(default=0)),
                ('p17', models.IntegerField(default=0)),
                ('p18', models.IntegerField(default=0)),
                ('p19', models.IntegerField(default=0)),
                ('p20', models.IntegerField(default=0)),
                ('p21', models.IntegerField(default=0)),
                ('p22', models.IntegerField(default=0)),
                ('p23', models.IntegerField(default=0)),
                ('p24', models.IntegerField(default=0)),
                ('p25', models.IntegerField(default=0)),
                ('p2_1', models.TextField()),
                ('p2_2', models.TextField()),
                ('p2_3', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PreSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField(default=0)),
                ('fill_time', models.DateTimeField(auto_now_add=True)),
                ('p', models.IntegerField(default=0)),
                ('p_t', models.TextField()),
                ('p1', models.IntegerField(default=0)),
                ('p2', models.IntegerField(default=0)),
                ('p3', models.IntegerField(default=0)),
                ('p4', models.IntegerField(default=0)),
                ('p5', models.IntegerField(default=0)),
                ('p6', models.IntegerField(default=0)),
                ('p7', models.IntegerField(default=0)),
                ('p8', models.IntegerField(default=0)),
                ('p9', models.IntegerField(default=0)),
                ('p10', models.IntegerField(default=0)),
            ],
        ),
    ]
