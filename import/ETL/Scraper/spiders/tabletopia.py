import scrapy
from ..items import TTGameItem
from scrapy_splash import SplashRequest
#from scrapy.crawler import CrawlerProcess
#from scrapy.utils.project import get_project_settings
#from ..helper import get_bga_ids, get_board_game_names_and_ids
#from ..globals import *

# class TableTopiaGames(scrapy.Spider):
#     name = 'tt_games'
#     page = 1
#
#     start_urls = ['https://tabletopia.com/games?page='+str(page)+'&languageIds=34']
#
#     def start_requests(self):
#         for url in self.start_urls:
#             yield SplashRequest(url, self.parse,
#                                 endpoint='render.html',
#                                 args={'wait': 0.9},
#                                 )
#
#     def parse(self, response):
#         items = TTGameItem()
#
#         games = response.css('.catalog')
#
#         for game in games:
#             name = game.css('h3.item_title_flag').extract()
#             url = game.css('#user-reviews-text a.float-right::attr(href)').extract()
#
#             items['name'] = name
#             items['url'] = url
#             yield items
#
#         # increase index:
#         self.page += 1
#         # if list hasn't been finished yet
#         if self.page <= 34:
#             # change to next url:
#             next_page = 'https://tabletopia.com/games?page='+str(self.page)+'&languageIds=34'
#             yield response.follow(next_page, callback=self.parse)

