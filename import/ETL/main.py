# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from ETL.Integration.auxiliary_tables import auxiliary_tables
from ETL.globals import *
from ETL.Cleaning.BoardGameAtlas.clean_boardgameatlas_data import clean_bga_api_review_data, clean_bga_api_game_information, \
    create_list_of_ids_of_all_bga_games
from ETL.Cleaning.BoardGameGeeks.clean_boardgamegeeks_data import clean_bgg_games, clean_bgg_reviews
from ETL.Integration.bgg_and_bga_integration import match_game_names, merge_game_information, merge_reviews, extract_users, \
    clean_reviews
from ETL.API.bga_api import get_bga_game_information_from_api, get_bga_mechanics, get_bga_categories
from datetime import datetime


def pipeline():
    """
    1)  Spider: GameInformation
        1.1: Crawl BoardGameAtlas.com to get IDs of all BoardGamesAtlas Games
        1.2: Clean Spider Results
        1.3: Extract IDs

    2)  API: GameInformation
        2.1: Get all information for all 120k games provided by BGA games API
        2.2: Clean API GameInformation data
        2.3: Create "auxiliary tables" for publishers, designers, categories and mechanics
        2.4: Get Ids of Games with >= 3 ratings

    3)  API: GameReviews
        3.1: Get all 162k reviews for games with >= ratings provided by BGA reviews API
        3.2: Clean API GameReviews data

    4)  Kaggle Dataset BGG: Reviews
        4.1: Clean Data

    5)  Kaggle Dataset BGG: GameInformation
        5.1: Clean Data

    6)  Data Integration:
        6.1:
    """

    print('Hello World!')

    if RUN_PIPELINE_SPIDER:
        # runSpider()
        # clean_bga_game_information_scraper()
        create_list_of_ids_of_all_bga_games()
        print('Spider Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))

    if RUN_BGA_GAME_INFO_API_PIPELINE:
        # get_bga_game_information_from_api()
        # get_bga_mechanics()
        # get_bga_categories()
        clean_bga_api_game_information()
        # create_id_list_of_included_games()
        print('BGA Game Info API Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))

    if RUN_BGA_REVIEWS_API_PIPELINE:
        # bga_review_api_main()
        # clean_bga_api_review_data()
        print('BGA Game Review API Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))

    if RUN_BGG_CLEANING_PIPELINE:
        # clean_bgg_games()
        # clean_bgg_reviews()
        print('BGG Cleaning Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))

    if RUN_INTEGRATION_PIPELINE:
        match_game_names()
        # merge_game_information()
        # merge_reviews()
        # extract_users()
        # clean_reviews()
        auxiliary_tables()

        print('Integration pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pipeline()


#######################################################################################
#
# Command line cheat sheet:
#   Start crawling:
#   cd BoardGameRecommender           (...\BoardGameRecommender\BoardGameRecommender)
#   scrapy crawl bga
#   scrapy crawl bga -o "test.json"
#
#   Scrapy shell for manual testing:
#   scrapy shell "https://www.boardgameatlas.com"
#
#   Docker:
#   $ docker pull scrapinghub/splash
#   $ docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
#
#######################################################################################