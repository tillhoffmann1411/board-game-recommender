from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

from games.models import BoardGame


class UserTaste(models.Model):
    username = models.CharField(max_length=80)
    number_of_reviews = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Review(models.Model):
    game = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserTaste, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(10)])
    text = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    origin = models.CharField(max_length=10)
