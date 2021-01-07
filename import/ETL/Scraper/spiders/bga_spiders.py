import scrapy
from ..items import BgaBoardGameItem, BgaReviewUrlItem, BgaRatingsItem, BgaCommentsItem, BgaPublishersItem, TTGameItem
from scrapy_splash import SplashRequest
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# from ...helper import get_bga_ids_of_all_games, get_board_game_names_and_ids, get_bga_publishers
# from ...globals import *
import pandas as pd


# related to BgaBoardGameSpider
NUM_GAMES_TO_SCRAPE = 120000
STARTING_POINT = 0


def get_bga_publishers():
    import_path = '../Data/BoardGameAtlas/Processed/API/BGA_All_Unique_Publishers.csv'
    publishers = pd.read_csv(import_path, index_col=0)

    pub_list = publishers.values.tolist()

    return pub_list


class BgaPublisherSpider(scrapy.Spider):
    name = 'publisherSpider'
    publishers = get_bga_publishers()

    index = 0
    start_urls = publishers[index][1]


    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                                endpoint='render.html',
                                args={'wait': 0.9},
                                )

    def parse(self, response):
        items = BgaRatingsItem()

        publisher_url = response.url

        publisher_name = response.css('h1::text').extract()
        publisher_bga_image_url = response.css('.mb-2 .w-100::attr(src').extract()

        items['publisher_name'] = publisher_name
        items['publisher_bga_image_url'] = publisher_bga_image_url
        items['publisher_url'] = publisher_url

        yield items

        # increase index:
        self.index += 1
        # if list hasn't been finished yet
        if self.index < len(self.ids):
            # change to next url:
            next_page = self.publishers[self.index][1]
            yield response.follow(next_page, callback=self.parse)


class BgaBoardGameSpider(scrapy.Spider):
    name = 'boardGameSpider'

    # batch parameters:
    starting_point = STARTING_POINT
    num_games_to_scrape = NUM_GAMES_TO_SCRAPE

    batch_size = 100
    current_batch = 1
    skip_nr = batch_size * (current_batch - 1) + starting_point

    start_urls = ['https://www.boardgameatlas.com/search/?skip=' + str(skip_nr) + '&q=']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                                endpoint='render.html',
                                args={'wait': 0.9},
                                )

    def parse(self, response):
        items = BgaBoardGameItem()

        games = response.css('.game-item')

        for game in games:
            # Scrape "Search" Page
            name = game.css('.game-importance strong a').css('::text').extract()
            score = game.css('.high').css('::text').extract()
            rank = game.css('.ml-1:nth-child(1)').css('::text').extract()
            num_players_and_play_time = game.css('.d-lg-none div:nth-child(1)').css('::text').extract()
            author = game.css('.mdi-pencil+ a').css('::text').extract()
            publisher = game.css('.mdi-truck+ a').css('::text').extract()
            image_link = game.css('img::attr(src)').extract()
            bga_game_id = game.css('.game-item::attr(id)').extract()
            url = response.url

            items['name'] = name
            items['score'] = score
            items['rank'] = rank

            # num_plyers and play_time will have to be split later on in a cleaning step!
            items['num_players_and_play_time'] = num_players_and_play_time
            items['author'] = author
            items['publisher'] = publisher
            items['image_link'] = image_link

            # IDs look like this: game-TAAifFP590
            # => the first part "game-" has to be cut out in a cleaning step later on!
            items['bga_game_id'] = bga_game_id
            items['url'] = url

            yield items

        # Change the URL so that the next page is crawled.
        self.skip_nr = self.batch_size * (self.current_batch - 1) + self.starting_point
        next_page = 'https://www.boardgameatlas.com/search/?skip=' + str(self.skip_nr) + '&q='

        # If desired number of batches isn't reached yet, recursive call of next page.
        if self.current_batch <= self.num_games_to_scrape // self.batch_size:
            self.current_batch += 1

            yield response.follow(next_page, callback=self.parse)


# class BgaReviewUrlCrawler(scrapy.Spider):
#     name = 'reviewCrawler'
#     index = 0
#
#     ids = get_bga_ids_of_all_games()
#
#     start_urls = ['https://www.boardgameatlas.com/game/' + str(ids[index]) + '/']
#
#     def start_requests(self):
#         for url in self.start_urls:
#             yield SplashRequest(url, self.parse,
#                                 endpoint='render.html',
#                                 args={'wait': 0.9},
#                                 )
#
#     def parse(self, response):
#         items = BgaReviewUrlItem()
#
#         url = response.css('#user-reviews-text a.float-right::attr(href)').extract()
#
#         items['url'] = url
#         yield items
#
#         # increase index:
#         self.index += 1
#         # if list hasn't been finished yet
#         if self.index < len(self.ids):
#             # change to next url:
#             next_page = 'https://www.boardgameatlas.com/game/' + str(self.ids[self.index]) + '/'
#             yield response.follow(next_page, callback=self.parse)
#
#
# class BgaRatingSpider(scrapy.Spider):
#     name = 'ratingSpider'
#     index = 0
#
#     names_and_ids = get_board_game_names_and_ids()
#
#     start_urls = ['https://www.boardgameatlas.com/game/' +
#                   str(names_and_ids[index]['bga_game_id']) + '/' +
#                   str(names_and_ids[index]['name']) +
#                   '/reviews']
#
#     def start_requests(self):
#         for url in self.start_urls:
#             yield SplashRequest(url, self.parse,
#                                 endpoint='render.html',
#                                 args={'wait': 0.9},
#                                 )
#
#     def parse(self, response):
#         items = BgaRatingsItem()
#
#         # clean: 'Wingspan Reviews' -> 'Wingspan'
#         name = response.css('.card-body.mb-3 a').css('::text').extract()
#
#         # clean: extract from 'https://www.boardgameatlas.com/game/TAAifFP590/root/reviews' -> 'TAAifFP590'
#         bga_game_id = response.url
#
#         url = response.url
#
#         # clean: extract from 'Rating Summary (357 Total)' -> '357'
#         num_ratings = response.css('.rating-summary h4').css('::text').extract()
#
#         # clean: extract from 'Wingspan has 357 reviews with an average rating of 4.00 / 5.' -> '4.00'
#         avg_rating = response.css('.mb-3 p').css('::text').extract()
#
#         num_one_star_rating = response.css('.one-star').css('::text').extract()
#         num_two_star_rating = response.css('.two-star').css('::text').extract()
#         num_three_star_rating = response.css('.three-star').css('::text').extract()
#         num_four_star_rating = response.css('.four-star').css('::text').extract()
#         num_five_star_rating = response.css('.five-star').css('::text').extract()
#
#         items['name'] = name
#         items['bga_game_id'] = bga_game_id
#         items['url'] = url
#         items['num_ratings'] = num_ratings
#         items['avg_rating'] = avg_rating
#         items['num_one_star_rating'] = num_one_star_rating
#         items['num_two_star_rating'] = num_two_star_rating
#         items['num_three_star_rating'] = num_three_star_rating
#         items['num_four_star_rating'] = num_four_star_rating
#         items['num_five_star_rating'] = num_five_star_rating
#
#         yield items
#
#         # increase index:
#         self.index += 1
#
#         # if list hasn't been finished yet
#         if self.index < len(self.names_and_ids):
#             # change next url:
#             next_page = 'https://www.boardgameatlas.com/game/' \
#                         + str(self.names_and_ids[self.index]['bga_game_id']) + '/' \
#                         + str(self.names_and_ids[self.index]['name']) \
#                         + '/reviews'
#
#             yield response.follow(next_page, callback=self.parse)
#
#
# class BgaCommentSpider(scrapy.Spider):
#     name = 'commentSpider'
#     index = 0
#
#     names_and_ids = get_board_game_names_and_ids()
#
#     start_urls = ['https://www.boardgameatlas.com/game/' +
#                   str(names_and_ids[index]['bga_game_id']) + '/' +
#                   str(names_and_ids[index]['name']) +
#                   '/reviews']
#
#     def start_requests(self):
#         for url in self.start_urls:
#             yield SplashRequest(url, self.parse,
#                                 endpoint='render.html',
#                                 args={'wait': 0.9},
#                                 )
#
#     def parse(self, response):
#         items = BgaCommentsItem()
#
#         comments = response.css('.card .card-body')
#
#         for comment in comments:
#             # clean: 'Wingspan Reviews' -> 'Wingspan'
#             name = response.css('.card-body.mb-3 a').css('::text').extract()
#
#             # clean: extract from 'https://www.boardgameatlas.com/game/TAAifFP590/root/reviews' -> 'TAAifFP590'
#             bga_game_id = response.url
#             url = response.url
#
#             comment_rating = comment.css('.card-body .stars::attr(data-rating)').extract()
#             comment_username = comment.css('.text-muted a').css('::text').extract()
#             comment_text = response.css('.card .card-body p').css('::text').extract()
#             comment_date = comment.css('.mt-3').css('::text').extract()
#
#             items['bga_game_id'] = bga_game_id
#             items['name'] = name
#             items['url'] = url
#             items['comment_rating'] = comment_rating
#             items['comment_username'] = comment_username
#             items['comment_text'] = comment_text
#             items['comment_date'] = comment_date
#
#             yield items
#
#         # increase index:
#         self.index += 1
#
#         # if list hasn't been finished yet
#         if self.index < len(self.names_and_ids):
#             # change next url:
#             next_page = 'https://www.boardgameatlas.com/game/' \
#                         + str(self.names_and_ids[self.index]['bga_game_id']) + '/' \
#                         + str(self.names_and_ids[self.index]['name']) \
#                         + '/reviews'
#
#             yield response.follow(next_page, callback=self.parse)
#
#
#
# # Start process from script instead of command line
# def run_bga_spiders():
#     process = CrawlerProcess(get_project_settings())
#
#     if RUN_BOARD_GAME_SPIDER:
#         process.crawl(BgaBoardGameSpider)
#     elif RUN_REVIEW_URL_CRAWLER:
#         process.crawl(BgaReviewUrlCrawler)
#     elif RUN_RATING_SPIDER:
#         process.crawl(BgaRatingSpider)
#     elif RUN_COMMENT_SPIDER:
#         process.crawl(BgaCommentSpider)
#
#     process.start()
#     print("Scraping finished!")


def scrape_publishers():
    process = CrawlerProcess(get_project_settings())
    process.crawl(BgaPublisherSpider)
    process.start()
    print("Finished scraping BGA publishers!")

