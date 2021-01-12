from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

from games.models import BoardGame


class UserTaste(models.Model):
    username = models.CharField(max_length=80)
    number_of_ratings = models.PositiveIntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    origin = models.CharField(max_length=10, blank=True, null=True)


class Review(models.Model):
    game = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserTaste, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(10)], blank=True, null=True)
    text = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    origin = models.CharField(max_length=10, blank=True, null=True)
