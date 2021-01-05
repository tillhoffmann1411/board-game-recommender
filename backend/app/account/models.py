from django.db import models
from django.contrib.auth.models import User

from game.models import BoardGame


class Taste(models.Model):
    games = models.ManyToManyField(BoardGame, related_name='taste')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
