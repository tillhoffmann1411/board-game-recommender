from .models import BoardGame
from rest_framework import serializers

# convert the received data from JSON format to the relative Django model and viceversa


class BoardGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardGame
        fields = ('id', 'name', 'image_url', 'year_published', 'min_playtime', 'max_playtime',
                  'bga_price_us', 'min_number_of_players', 'max_number_of_players', 'min_age', 'bgg_id')
