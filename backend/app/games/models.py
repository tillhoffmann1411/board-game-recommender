from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey


class Author(models.Model):
    id = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    bga_url = models.URLField(max_length=200, blank=True, null=True)


class Publisher(models.Model):
    id = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    bga_url = models.URLField(max_length=200, blank=True, null=True)


class GameMechanic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    bga_id = models.CharField(max_length=256, blank=True, null=True)
    bga_name = models.CharField(max_length=256, blank=True, null=True)
    bga_url = models.URLField(max_length=256, blank=True, null=True)
    bgg_id = models.PositiveIntegerField(blank=True, null=True)
    bgg_name = models.CharField(max_length=256, blank=True, null=True)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    bga_id = models.CharField(max_length=256, blank=True, null=True)
    bga_name = models.CharField(max_length=256, blank=True, null=True)
    bga_url = models.URLField(max_length=256, blank=True, null=True)
    bgg_id = models.PositiveIntegerField(blank=True, null=True)
    bgg_name = models.CharField(max_length=256, blank=True, null=True)


class OnlineGame(models.Model):
    # main
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1000, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    year_published = models.PositiveIntegerField(blank=True, null=True)
    min_playtime = models.PositiveSmallIntegerField(blank=True, null=True)
    max_playtime = models.PositiveSmallIntegerField(blank=True, null=True)
    min_number_of_players = models.PositiveSmallIntegerField(blank=True, null=True)
    max_number_of_players = models.PositiveSmallIntegerField(blank=True, null=True)
    min_age = models.PositiveSmallIntegerField(blank=True, null=True)

    # Relations
    author = ForeignKey(Author, on_delete=models.SET_NULL, blank=True, null=True)
    publisher = ForeignKey(Publisher, on_delete=models.SET_NULL, blank=True, null=True)
    game_mechanic = ForeignKey(GameMechanic, on_delete=models.SET_NULL, blank=True, null=True)
    category = ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)


class BoardGame(models.Model):
    # main
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1000, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    year_published = models.PositiveIntegerField(blank=True, null=True)
    min_playtime = models.PositiveSmallIntegerField(blank=True, null=True)
    max_playtime = models.PositiveSmallIntegerField(blank=True, null=True)
    min_number_of_players = models.PositiveSmallIntegerField(blank=True, null=True)
    max_number_of_players = models.PositiveSmallIntegerField(blank=True, null=True)
    min_age = models.PositiveSmallIntegerField(blank=True, null=True)

    # Relations
    author = ForeignKey(Author, on_delete=models.SET_NULL, blank=True, null=True)
    publisher = ForeignKey(Publisher, on_delete=models.SET_NULL, blank=True, null=True)
    game_mechanic = ForeignKey(GameMechanic, on_delete=models.SET_NULL, blank=True, null=True)
    category = ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    # Similar Online Games
    similar_online_games = models.ManyToManyField(OnlineGame, through='SimilarBoardOnlineGame')

    # BGG stuff
    bgg_id = models.IntegerField(blank=True, null=True)
    bgg_avg_rating = models.FloatField(blank=True, null=True)
    bgg_num_ratings = models.PositiveIntegerField(blank=True, null=True)
    bgg_avg_bayes = models.FloatField(blank=True, null=True)
    bgg_rank = models.PositiveSmallIntegerField(blank=True, null=True)
    bgg_stddev = models.FloatField(blank=True, null=True)
    bgg_num_user_comments = models.PositiveSmallIntegerField(blank=True, null=True)

    # BGA stuff
    bga_id = models.CharField(max_length=256, blank=True, null=True)
    bga_avg_rating = models.FloatField(blank=True, null=True)
    bga_num_ratings = models.PositiveIntegerField(blank=True, null=True)
    bga_url = models.URLField(max_length=200, blank=True, null=True)
    bga_rank = models.IntegerField(blank=True, null=True)
    bga_rank_trending = models.PositiveSmallIntegerField(blank=True, null=True)
    bga_price_us = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # others
    thumbnail_url = models.URLField(max_length=200, blank=True, null=True)
    official_url = models.URLField(max_length=200, blank=True, null=True)
    reddit_all_time_count = models.PositiveSmallIntegerField(blank=True, null=True)


class SimilarBoardOnlineGame(models.Model):
    online_game = models.ForeignKey(OnlineGame, on_delete=models.CASCADE)
    board_game = models.ForeignKey(BoardGame, on_delete=CASCADE)
