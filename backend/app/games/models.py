from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib.auth.models import User


class Author(models.Model):
    id = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)


class Publisher(models.Model):
    id = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)


class GameMechanic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    bga_url = models.URLField(max_length=256, blank=True, null=True)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    bga_url = models.URLField(max_length=256, blank=True, null=True)


class OnlineGame(models.Model):
    # main
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    url = models.URLField(max_length=500, blank=True, null=True)
    origin = models.CharField(max_length=256, blank=True, null=True)
    bgg_id = models.IntegerField(blank=True, null=True)


class BoardGame(models.Model):
    # main
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    year_published = models.FloatField(blank=True, null=True)
    min_playtime = models.FloatField(blank=True, null=True)
    max_playtime = models.FloatField(blank=True, null=True)
    min_number_of_players = models.FloatField(blank=True, null=True)
    max_number_of_players = models.FloatField(blank=True, null=True)
    min_age = models.FloatField(blank=True, null=True)

    # Relations
    author = ManyToManyField(Author, through='BoardgameAuthor')
    publisher = ManyToManyField(Publisher, through='BoardgamePublisher')
    game_mechanic = ManyToManyField(GameMechanic, through='BoardgameMechanic')
    category = ManyToManyField(Category, through='BoardgameCategory')
    # Recommendations
    user_recommendations = models.ManyToManyField(User, through='Recommendations')

    # BGG stuff
    bgg_id = models.FloatField(blank=True, null=True)
    bgg_avg_rating = models.FloatField(blank=True, null=True)
    bgg_num_ratings = models.FloatField(blank=True, null=True)
    bgg_avg_bayes = models.FloatField(blank=True, null=True)
    bgg_rank = models.FloatField(blank=True, null=True)
    bgg_stddev = models.FloatField(blank=True, null=True)
    bgg_num_user_comments = models.FloatField(blank=True, null=True)

    # BGA stuff
    bga_id = models.CharField(max_length=256, blank=True, null=True)
    bga_avg_rating = models.FloatField(blank=True, null=True)
    bga_num_ratings = models.FloatField(blank=True, null=True)
    bgg_average_weight = models.FloatField(blank=True, null=True)
    bga_url = models.URLField(max_length=500, blank=True, null=True)
    bga_rank = models.FloatField(blank=True, null=True)
    bga_rank_trending = models.FloatField(blank=True, null=True)
    bga_price_us = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)

    # others
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    official_url = models.URLField(max_length=500, blank=True, null=True)
    reddit_all_time_count = models.FloatField(blank=True, null=True)


class Recommendations(models.Model):
    board_game = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ItemSimilarityMatrix(models.Model):
    game_one = models.FloatField()
    game_two = models.FloatField()
    similarity = models.FloatField()

    class Meta:
        indexes = [models.Index(fields=['game_one'])]


class BoardgameAuthor(models.Model):
    boardgame = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class BoardgamePublisher(models.Model):
    boardgame = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)


class BoardgameMechanic(models.Model):
    boardgame = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(GameMechanic, on_delete=models.CASCADE)


class BoardgameCategory(models.Model):
    boardgame = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
