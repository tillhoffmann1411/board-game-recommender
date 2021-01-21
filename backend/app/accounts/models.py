from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db.models.signals import post_save

from games.models import BoardGame

# from https://stackoverflow.com/questions/11909877/django-user-save-hook
# Create a UserTaste entity when a new user registers


def check_superuser(sender, instance, signal, *args, **kwargs):
    if sender is User:
        UserTaste.objects.create(number_of_ratings=0, user=instance, origin='boreg')


post_save.connect(check_superuser, sender=User)


class UserTaste(models.Model):
    username = models.CharField(max_length=80, blank=True, null=True)
    number_of_ratings = models.PositiveIntegerField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    origin = models.CharField(max_length=10, blank=True, null=True)


class Review(models.Model):
    game = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserTaste, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MaxValueValidator(10)], blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    origin = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = [['created_by', 'game']]
