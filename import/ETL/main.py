from ETL.Integration.auxiliary_tables import integrate_auxiliary_tables
# from ETL.Integration.onlinegames_tables_integration import match_online_game_names_and_bgg_names, integrate_online_games
from ETL.Integration.onlinegames_tables_integration import merge_online_games, match_online_game_names_and_bgg_names
from ETL.Load.load_to_db import upload_users_to_db, upload_board_games_to_db, upload_reviews_to_db, upload_categories_to_db, \
    upload_gamemechanic_to_db, upload_publisher_to_db, upload_author_to_db, upload_online_games_to_db, upload_similarity_matrix_to_db
from ETL.globals import *
from ETL.Cleaning.BoardGameAtlas.clean_boardgameatlas_data import clean_bga_api_review_data, clean_bga_api_game_information, \
    create_list_of_ids_of_all_bga_games, create_id_list_of_included_bga_games, clean_bga_game_information_scraper
from ETL.Cleaning.BoardGameGeeks.clean_boardgamegeeks_data import clean_bgg_games, clean_bgg_reviews
from ETL.Integration.bgg_and_bga_integration import integrate_boardgame_table, integrate_user_and_review_tables
from ETL.API.bga_api import get_bga_game_information_from_api, get_bga_mechanics_from_api, get_bga_categories_from_api
from datetime import datetime


def etl_pipeline():
    """
    Find a detailed overview of what function does what in the ETL pipeline below.
    Adjust the boolean "flags" in the globals.py to only run certain parts of the pipeline.

    1)  BoardGameAtlas (BGA)
        1.1: BGA Scraper
            1.1.1: Crawl BoardGameAtlas.com to get IDs of all BoardGamesAtlas Games
            1.1.2: Extract BGA IDs from scraped data to use them for the API calls
        1.2: BGA API
            1.2.1: BGA Board Games
                1.2.1.1: Get all information for all 120k games provided by BGA games API
                1.2.1.2: Clean API GameInformation data (includes creating "auxiliary" tables for publishers,
                         designers, categories, mechanics, ...)
                1.2.1.3: Create a list of the IDs of all obtained BGA games. This list is later used to when
                         requesting reviews from the BGA API.
                1.2.1.4: Get all BGA game mechanics
                1.2.1.5: Get all BGA game categories
            1.2.2: BGA Reviews
                1.2.2.1: Get all 162k reviews for games with >= 3 ratings provided by BGA reviews API
                1.2.2.2: Clean API GameReviews data

    2)  BoardGameGeeks (BGG):
        2.1: Clean BGG GameInformation and create "auxiliary tables" for publishers, designers, categories and mechanics
        2.2: Clean BGG Reviews

    3)  OnlineGames:
        3.1: Scrape Tabletopia Games
        3.2: Scrape BoardGameArena Games
        3.3: Scrape Yucata Games

    4)  OfflineGames (BGA & BGG) Integration:
        4.1: Integrate BGA and BGG boardgame table by matching game names
        4.2: Integrate BGA and BGG reviews and create integrated user table
        4.3: Integrates the auxiliary tables publishers, designers, categories, mechanics and GameNameTranslations

    5)  OnlineGames Integration:
        5.1: Integrate online games
        5.2: Link online games to offline games

    6)  Load to Database:
        6.1: Upload users
        6.2: Upload board games
        6.3: Upload reviews
        6.4: Upload categories
        6.5: Upload mechanics
        6.6: Upload publishers
        6.7: Upload designers/authors
        6.8: Upload online games
    """

    if RUN_BGA_PIPELINE:
        ### BGA Scraper: ###
        # runSpider()
        create_list_of_ids_of_all_bga_games()
        print('Scraper Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))

        ### BGA API - Board Games: ###
        # get_bga_game_information_from_api()
        clean_bga_api_game_information()
        create_id_list_of_included_bga_games()
        # get_bga_mechanics_from_api()
        # get_bga_categories_from_api()
        print('BGA Board Games API Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))

        ### BGA API - Reviews: ###
        # bga_review_api_main()
        clean_bga_api_review_data()
        print('BGA Game Reviews API Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))


    if RUN_BGG_PIPELINE:
        clean_bgg_games()
        clean_bgg_reviews()
        print('BGG Cleaning Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))


    if RUN_SCRAPE_ONLINE_GAMES_PIPELINE:

        ##### HIER ONLINE GAMES SCRAPER FUNKTIONEN EINFÜGEN #####

        print('Scrape Online Games Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))


    if RUN_INTEGRATE_OFFLINE_GAMES_PIPELINE:
        # integrate_boardgame_table()
        # integrate_user_and_review_tables()
        # integrate_auxiliary_tables()
        print('Offline Games Integration Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))


    if RUN_INTEGRATE_ONLINE_GAMES_PIPELINE:
        merge_online_games()
        match_online_game_names_and_bgg_names()
        print('Online Games Integration Pipeline completed! ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))


    if RUN_UPLOAD:
        # upload_users_to_db()
        # upload_board_games_to_db()
        # upload_reviews_to_db()

        upload_categories_to_db()
        upload_gamemechanic_to_db()
        upload_publisher_to_db()
        upload_author_to_db()

        # upload_online_games_to_db()


        # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    etl_pipeline()




#######################################################################################
#
# Command line cheat sheet Scrapy:
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
