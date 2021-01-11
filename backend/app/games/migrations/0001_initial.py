# Generated by Django 3.0.11 on 2021-01-09 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.CharField(max_length=80, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('bga_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='BoardGame',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('description', models.CharField(max_length=1000)),
                ('image_url', models.URLField()),
                ('year_published', models.PositiveIntegerField()),
                ('min_playtime', models.PositiveSmallIntegerField()),
                ('max_playtime', models.PositiveSmallIntegerField()),
                ('min_number_of_players', models.PositiveSmallIntegerField()),
                ('max_number_of_players', models.PositiveSmallIntegerField()),
                ('min_age', models.PositiveSmallIntegerField()),
                ('bgg_id', models.IntegerField()),
                ('bgg_avg_rating', models.FloatField()),
                ('bgg_num_ratings', models.PositiveIntegerField()),
                ('bgg_avg_bayes', models.FloatField()),
                ('bgg_rank', models.PositiveSmallIntegerField()),
                ('bgg_stddev', models.FloatField()),
                ('bgg_num_user_comments', models.PositiveSmallIntegerField()),
                ('bga_id', models.CharField(max_length=80)),
                ('bga_avg_rating', models.FloatField()),
                ('bga_num_ratings', models.PositiveIntegerField()),
                ('bga_url', models.URLField()),
                ('bga_rank', models.IntegerField()),
                ('bga_rank_trending', models.PositiveSmallIntegerField()),
                ('bga_price_us', models.DecimalField(decimal_places=2, max_digits=5)),
                ('thumbnail_url', models.URLField()),
                ('official_url', models.URLField()),
                ('reddit_all_time_count', models.PositiveSmallIntegerField()),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('bga_id', models.CharField(max_length=80)),
                ('bga_name', models.CharField(max_length=80)),
                ('bga_url', models.URLField()),
                ('bgg_id', models.PositiveIntegerField()),
                ('bgg_name', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='GameMechanic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('bga_id', models.CharField(max_length=80)),
                ('bga_name', models.CharField(max_length=80)),
                ('bga_url', models.URLField()),
                ('bgg_id', models.PositiveIntegerField()),
                ('bgg_name', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='OnlineGame',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('description', models.CharField(max_length=1000)),
                ('image_url', models.URLField()),
                ('year_published', models.PositiveIntegerField()),
                ('min_playtime', models.PositiveSmallIntegerField()),
                ('max_playtime', models.PositiveSmallIntegerField()),
                ('min_number_of_players', models.PositiveSmallIntegerField()),
                ('max_number_of_players', models.PositiveSmallIntegerField()),
                ('min_age', models.PositiveSmallIntegerField()),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.Author')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.Category')),
                ('game_mechanic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.GameMechanic')),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.CharField(max_length=80, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('bga_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='SimilarBoardOnlineGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board_game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.BoardGame')),
                ('online_game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.OnlineGame')),
            ],
        ),
        migrations.AddField(
            model_name='onlinegame',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.Publisher'),
        ),
        migrations.AddField(
            model_name='boardgame',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.Category'),
        ),
        migrations.AddField(
            model_name='boardgame',
            name='game_mechanic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.GameMechanic'),
        ),
        migrations.AddField(
            model_name='boardgame',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.Publisher'),
        ),
        migrations.AddField(
            model_name='boardgame',
            name='similar_online_games',
            field=models.ManyToManyField(through='games.SimilarBoardOnlineGame', to='games.OnlineGame'),
        ),
    ]
