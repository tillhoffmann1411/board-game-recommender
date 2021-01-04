# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy



# Boardgameatlas:

class BgaBoardGameItem(scrapy.Item):
    name = scrapy.Field()
    score = scrapy.Field()
    rank = scrapy.Field()
    num_players_and_play_time = scrapy.Field()
    author = scrapy.Field()
    publisher = scrapy.Field()
    image_link = scrapy.Field()
    bga_game_id = scrapy.Field()
    url = scrapy.Field()


class BgaReviewUrlItem(scrapy.Item):
    url = scrapy.Field()


class BgaRatingsItem(scrapy.Item):
    name = scrapy.Field()
    bga_game_id = scrapy.Field()
    url = scrapy.Field()
    num_ratings = scrapy.Field()
    avg_rating = scrapy.Field()
    num_one_star_rating = scrapy.Field()
    num_two_star_rating = scrapy.Field()
    num_three_star_rating = scrapy.Field()
    num_four_star_rating = scrapy.Field()
    num_five_star_rating = scrapy.Field()


class BgaCommentsItem(scrapy.Item):
    bga_game_id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    comment_rating = scrapy.Field()
    comment_username = scrapy.Field()
    comment_text = scrapy.Field()
    comment_date = scrapy.Field()


class BgaPublishersItem(scrapy.Item):
    publisher_name = scrapy.Field()
    publisher_bga_image_url = scrapy.Field()
    publisher_url = scrapy.Field()


# Tabletopia:

class TTGameItem(scrapy.Item):
    name = scrapy.Field()
    image_url = scrapy.Field()
    # tags = scrapy.Field()
    # age_recommendation = scrapy.Field()
    # numPlayers = scrapy.Field()
    # playTime = scrapy.Field()
    # rating = scrapy.Field()

