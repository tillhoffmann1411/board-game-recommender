# Generated by Django 3.0.11 on 2021-01-26 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_auto_20210126_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemSimilarityMatrix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_one', models.IntegerField()),
                ('game_two', models.IntegerField()),
                ('similarity', models.FloatField()),
            ],
        ),
    ]
