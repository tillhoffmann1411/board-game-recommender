from .models import Author, BoardGame, Category, GameMechanic, OnlineGame, Publisher, Recommendations
from rest_framework import serializers
import math


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendations
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MechanicSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameMechanic
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


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
        fields = ('id', 'name', 'image_url', 'min_playtime', 'max_playtime', 'min_number_of_players',
                  'max_number_of_players', 'min_age')

    # Unused fields:    'reddit_all_time_count', 'author', 'category', 'game_mechanic', 'publisher',
    #                   'bga_rank_trending', 'bga_rank', 'bgg_average_wight', 'bga_num_ratings', 'bga_id',
    #                   'bgg_num_user_comments', 'bgg_stddev', 'bgg_rank', 'bgg_avg_bayes', 'bbg_num_ratings', 'bgg_id'

    # From: https://stackoverflow.com/questions/52169173/django-rest-framework-how-to-substitute-null-with-empty-string
    # This function helps to make Float values (-> NaN) JSON compatible
    def to_representation(self, instance):
        my_fields = {'id', 'name', 'image_url', 'min_playtime', 'max_playtime',
                     'min_number_of_players', 'max_number_of_players', 'min_age'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if isinstance(data[field], float) and math.isnan(data[field]):
                    data[field] = 0
            except KeyError:
                pass
        return data


class BoardGameDetailSerializer(BoardGameSerializer):
    category = CategorySerializer(read_only=True, many=True)
    game_mechanic = MechanicSerializer(read_only=True, many=True)
    author = AuthorSerializer(read_only=True, many=True)
    publisher = PublisherSerializer(read_only=True, many=True)

    class Meta:
        model = BoardGame
        fields = ('id', 'name', 'description', 'image_url', 'year_published', 'min_playtime', 'max_playtime',
                  'bga_price_us', 'min_number_of_players', 'max_number_of_players', 'min_age',
                  'bgg_avg_rating', 'bga_avg_rating', 'bga_url', 'thumbnail_url', 'official_url', 'bga_rank',
                  'bgg_rank', 'author', 'category', 'game_mechanic', 'publisher', 'bgg_id')

    # Unused fields:    'reddit_all_time_count', 'bga_rank_trending', 'bgg_average_wight', 'bga_num_ratings', 'bga_id',
    #                   'bgg_num_user_comments', 'bgg_stddev', 'bgg_avg_bayes', 'bbg_num_ratings'

    # From: https://stackoverflow.com/questions/52169173/django-rest-framework-how-to-substitute-null-with-empty-string
    # This function helps to make Float values (-> NaN) JSON compatible
    def to_representation(self, instance):
        my_fields = {'id', 'name', 'description', 'image_url', 'year_published', 'min_playtime', 'max_playtime',
                     'bga_price_us', 'min_number_of_players', 'max_number_of_players', 'min_age',
                     'bgg_avg_rating', 'bga_avg_rating', 'bga_url', 'thumbnail_url', 'official_url', 'bga_rank', 'bgg_rank'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if isinstance(data[field], float) and math.isnan(data[field]):
                    data[field] = 0
            except KeyError:
                pass
        return data


class OnlineGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineGame
        fields = '__all__'
