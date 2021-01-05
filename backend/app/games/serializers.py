from .models import BoardGame
from rest_framework import serializers

# convert the received data from JSON format to the relative Django model and viceversa


class BoardGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardGame
        fields = ('id', 'name', 'description', 'price')
