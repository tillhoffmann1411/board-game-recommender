from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey


class Author(models.Model):
    id = models.CharField(max_length=80, primary_key=True)
    name = models.CharField(max_length=80)
    bga_url = models.URLField(max_length=200)


class Publisher(models.Model):
    id = models.CharField(max_length=80, primary_key=True)
    name = models.CharField(max_length=80)
    bga_url = models.URLField(max_length=200)


class GameMechanic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    bga_id = models.CharField(max_length=80)
    bga_name = models.CharField(max_length=80)
    bga_url = models.URLField(max_length=200)
    bgg_id = models.PositiveIntegerField()
    bgg_name = models.CharField(max_length=80)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    bga_id = models.CharField(max_length=80)
    bga_name = models.CharField(max_length=80)
    bga_url = models.URLField(max_length=200)
    bgg_id = models.PositiveIntegerField()
    bgg_name = models.CharField(max_length=80)


class OnlineGame(models.Model):
    # main
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=1000)
    image_url = models.URLField(max_length=200)
    year_published = models.PositiveIntegerField()
    min_playtime = models.PositiveSmallIntegerField()
    max_playtime = models.PositiveSmallIntegerField()
    min_number_of_players = models.PositiveSmallIntegerField()
    max_number_of_players = models.PositiveSmallIntegerField()
    min_age = models.PositiveSmallIntegerField()

    # Relations
    author = ForeignKey(Author, on_delete=models.SET_NULL, blank=True, null=True)
    publisher = ForeignKey(Publisher, on_delete=models.SET_NULL, blank=True, null=True)
    game_mechanic = ForeignKey(GameMechanic, on_delete=models.SET_NULL, blank=True, null=True)
    category = ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)


class BoardGame(models.Model):
    # main
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=1000)
    image_url = models.URLField(max_length=200)
    year_published = models.PositiveIntegerField()
    min_playtime = models.PositiveSmallIntegerField()
    max_playtime = models.PositiveSmallIntegerField()
    min_number_of_players = models.PositiveSmallIntegerField()
    max_number_of_players = models.PositiveSmallIntegerField()
    min_age = models.PositiveSmallIntegerField()

    # Relations
    author = ForeignKey(Author, on_delete=models.SET_NULL, blank=True, null=True)
    publisher = ForeignKey(Publisher, on_delete=models.SET_NULL, blank=True, null=True)
    game_mechanic = ForeignKey(GameMechanic, on_delete=models.SET_NULL, blank=True, null=True)
    category = ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    # Similar Online Games
    similar_online_games = models.ManyToManyField(OnlineGame, through='SimilarBoardOnlineGame')

    # BGG stuff
    bgg_id = models.IntegerField()
    bgg_avg_rating = models.FloatField()
    bgg_num_ratings = models.PositiveIntegerField()
    bgg_avg_bayes = models.FloatField()
    bgg_rank = models.PositiveSmallIntegerField()
    bgg_stddev = models.FloatField()
    bgg_num_user_comments = models.PositiveSmallIntegerField()

    # BGA stuff
    bga_id = models.CharField(max_length=80)
    bga_avg_rating = models.FloatField()
    bga_num_ratings = models.PositiveIntegerField()
    bga_url = models.URLField(max_length=200)
    bga_rank = models.IntegerField()
    bga_rank_trending = models.PositiveSmallIntegerField()
    bga_price_us = models.DecimalField(max_digits=5, decimal_places=2)

    # others
    thumbnail_url = models.URLField(max_length=200)
    official_url = models.URLField(max_length=200)
    reddit_all_time_count = models.PositiveSmallIntegerField()


class SimilarBoardOnlineGame(models.Model):
    online_game = models.ForeignKey(OnlineGame, on_delete=models.CASCADE)
    board_game = models.ForeignKey(BoardGame, on_delete=CASCADE)
