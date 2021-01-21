from .models import BoardGame
from rest_framework import serializers
import math

# convert the received data from JSON format to the relative Django model and viceversa


class BoardGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardGame
        fields = ('id', 'name', 'image_url', 'year_published', 'min_playtime', 'max_playtime',
                  'bga_price_us', 'min_number_of_players', 'max_number_of_players', 'min_age',
                  'bgg_avg_rating', 'bga_avg_rating', 'bga_url', 'thumbnail_url', 'official_url')

    # Unused fields:    'reddit_all_time_count', 'author', 'category', 'game_mechanic', 'publisher',
    #                   'bga_rank_trending', 'bga_rank', 'bgg_average_wight', 'bga_num_ratings', 'bga_id',
    #                   'bgg_num_user_comments', 'bgg_stddev', 'bgg_rank', 'bgg_avg_bayes', 'bbg_num_ratings', 'bgg_id',

    # From: https://stackoverflow.com/questions/52169173/django-rest-framework-how-to-substitute-null-with-empty-string
    # This function helps to make Float values (-> NaN) JSON compatible
    def to_representation(self, instance):
        my_fields = {'id', 'name', 'image_url', 'year_published', 'min_playtime', 'max_playtime',
                     'bga_price_us', 'min_number_of_players', 'max_number_of_players', 'min_age',
                     'bgg_avg_rating', 'bga_avg_rating', 'bga_url', 'thumbnail_url', 'official_url'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if isinstance(data[field], float) and math.isnan(data[field]):
                    data[field] = 0
            except KeyError:
                pass
        return data
