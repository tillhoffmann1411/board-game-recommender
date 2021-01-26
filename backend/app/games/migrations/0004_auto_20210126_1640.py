# Generated by Django 3.0.11 on 2021-01-26 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_auto_20210125_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='onlinegame',
            name='author',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='category',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='description',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='game_mechanic',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='max_number_of_players',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='max_playtime',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='min_age',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='min_number_of_players',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='min_playtime',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='publisher',
        ),
        migrations.RemoveField(
            model_name='onlinegame',
            name='year_published',
        ),
        migrations.AddField(
            model_name='onlinegame',
            name='url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
