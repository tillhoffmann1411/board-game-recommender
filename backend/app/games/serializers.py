from .models import BoardGame, Recommendations
from rest_framework import serializers
import math


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class BoardGameSerializer(DynamicFieldsModelSerializer):
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


class BoardGameDetailSerializer(BoardGameSerializer):
    class Meta:
        model = BoardGame
        fields = ('id', 'name', 'description', 'image_url', 'year_published', 'min_playtime', 'max_playtime',
                  'bga_price_us', 'min_number_of_players', 'max_number_of_players', 'min_age',
                  'bgg_avg_rating', 'bga_avg_rating', 'bga_url', 'thumbnail_url', 'official_url')

    # Unused fields:    'reddit_all_time_count', 'author', 'category', 'game_mechanic', 'publisher',
    #                   'bga_rank_trending', 'bga_rank', 'bgg_average_wight', 'bga_num_ratings', 'bga_id',
    #                   'bgg_num_user_comments', 'bgg_stddev', 'bgg_rank', 'bgg_avg_bayes', 'bbg_num_ratings', 'bgg_id',

    # From: https://stackoverflow.com/questions/52169173/django-rest-framework-how-to-substitute-null-with-empty-string
    # This function helps to make Float values (-> NaN) JSON compatible
    def to_representation(self, instance):
        my_fields = {'id', 'year_published', 'min_playtime', 'max_playtime',
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


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendations
        fields = '__all__'
