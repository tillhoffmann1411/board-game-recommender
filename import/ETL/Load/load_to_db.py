from ETL.Load.postgres_helper import PostgresWrapper
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import logging
import os

load_dotenv()


def upload_users_to_db():
    # import users csv:
    users_df = pd.read_csv('../Data/Joined/Results/User.csv', index_col=0)

    # rename a few columns:
    users_df.rename(columns={'user_key': 'id',
                             'user_name': 'username',
                             'user_origin': 'origin',
                             'num_ratings': 'number_of_ratings',
                             }, inplace=True)

    # drop avg rating column:
    del users_df['avg_rating']

    upload_dataframe(users_df, 'accounts_usertaste')


def upload_board_games_to_db():
    # import boardgame csv:
    board_game_df = pd.read_csv(
        '../Data/Joined/Results/BoardGames.csv',
        index_col=0)

    # rename a few columns:
    board_game_df.rename(columns={'game_key': 'id',
                                  'game_description': 'description',
                                  'min_players': 'min_number_of_players',
                                  'max_players': 'max_number_of_players',
                                  'bgg_game_id': 'bgg_id',
                                  'bga_game_id': 'bga_id',
                                  'bgg_average_user_rating': 'bgg_avg_rating',
                                  'bga_average_user_rating': 'bga_avg_rating',
                                  'bgg_num_user_ratings': 'bgg_num_ratings',
                                  'bga_num_user_ratings': 'bga_num_ratings',
                                  'bga_game_url': 'bga_url',
                                  'bga_price_us_dollar': 'bga_price_us',
                                  'bga_trending_rank': 'bga_rank_trending'
                                  }, inplace=True)

    # drop some columns:
    del board_game_df['bgg_bayes_average']
    del board_game_df['main_designer_name']
    del board_game_df['main_designer_id']
    del board_game_df['main_designer_url']
    del board_game_df['main_publisher_name']
    del board_game_df['main_publisher_id']
    del board_game_df['main_publisher_url']

    upload_dataframe(board_game_df, 'games_boardgame')


def upload_reviews_to_db():
    # import users csv:
    reviews_df = pd.read_csv(
        '../Data/Joined/Results/Reviews.csv',
        index_col=0,
        dtype={
            'game_key': int,
            'user_key': int,
            'rating': float,
            'has_review_text': int,
            'user_origin': object
        },
        keep_default_na=False)

    # rename a few columns:
    reviews_df.rename(columns={'game_key': 'game_id',
                               'user_key': 'created_by_id',
                               'rating': 'rating',
                               'user_origin': 'origin'
                               }, inplace=True)

    # drop avg rating column:
    del reviews_df['has_review_text']

    upload_dataframe(reviews_df, 'accounts_review', 10000)


def upload_categories_to_db():
    # import users csv:
    categories_df = pd.read_csv(
        '../Data/Joined/Results/Categories.csv',
        index_col=0,
        dtype={
            'category_key': int,
            'categroy_bga_url': str,
            'category_name': str
        })

    # rename a few columns:
    categories_df.rename(columns={'category_key': 'id',
                                  'category_name': 'name',
                                  'category_bga_url': 'bga_url'
                                  }, inplace=True)

    upload_dataframe(categories_df, 'games_category')

    # import users csv:
    categories_relation_df = pd.read_csv(
        '../Data/Joined/Results/Category_Game_Relation.csv',
        index_col=0,
        dtype={
            'game_key': int,
            'category_key': int,
        })
    # rename a few columns:
    categories_relation_df.rename(columns={'game_key': 'boardgame_id',
                                  'category_key': 'category_id',
                                  }, inplace=True)

    upload_dataframe(categories_relation_df, 'games_boardgame_category')



def upload_gamemechanic_to_db():
    # import users csv:
    mechanic_df = pd.read_csv(
        '../Data/Joined/Results/Mechanics.csv',
        index_col=0,
        dtype={
            'mechanic_key': int,
            'mechanic_bga_url': str,
            'mechanic_name': str
        },
        keep_default_na=False)

    # rename a few columns:
    mechanic_df.rename(columns={'mechanic_key': 'id',
                                'mechanic_name': 'name',
                                'mechanic_bga_url': 'bga_url'
                                }, inplace=True)

    upload_dataframe(mechanic_df, 'games_gamemechanic')

    # import users csv:
    mechanic_relation_df = pd.read_csv(
        '../Data/Joined/Results/Mechanic_Game_Relation.csv',
        index_col=0,
        dtype={
            'game_key': int,
            'mechanic_key': int,
        })
    # rename a few columns:
    mechanic_relation_df.rename(columns={'game_key': 'boardgame_id',
                                           'mechanic_key': 'gamemechanic_id',
                                           }, inplace=True)

    upload_dataframe(mechanic_relation_df, 'games_boardgame_game_mechanic')


def upload_publisher_to_db():
    # import users csv:
    publisher_df = pd.read_csv(
        '../Data/Joined/Results/Publisher.csv',
        index_col=0,
        dtype={
            'publisher_key': int,
            'publisher_name': str,
            'publisher_image_url': str,
            'publisher_url': str,
            'publisher_bga_id': str,
            'publisher_bgg_key': int,
            'bgg_publisher_name': str,
        },
        keep_default_na=False)

    # rename a few columns:
    publisher_df.rename(columns={'publisher_key': 'id',
                                 'publisher_name': 'name',
                                 'publisher_image_url': 'image_url',
                                 'publisher_url': 'url',
                                 }, inplace=True)

    del publisher_df['publisher_bga_id']
    del publisher_df['publisher_bgg_key']
    del publisher_df['bgg_publisher_name']

    upload_dataframe(publisher_df, 'games_publisher')

    # import users csv:
    publisher_relation_df = pd.read_csv(
        '../Data/Joined/Results/Publisher_Game_Relation.csv',
        index_col=0,
        dtype={
            'game_key': int,
            'publisher_key': int,
        })
    # rename a few columns:
    publisher_relation_df.rename(columns={'game_key': 'boardgame_id',
                                  'publisher_key': 'publisher_id',
                                  }, inplace=True)

    upload_dataframe(publisher_relation_df, 'games_boardgame_publisher')


def upload_author_to_db():
    # import users csv:
    author_df = pd.read_csv(
        '../Data/Joined/Results/Designer.csv',
        index_col=0,
        dtype={
            'designer_key': int,
            'designer_name': str,
            'designer_image_url': str,
            'designer_url': str
        },
        keep_default_na=False)

    # rename a few columns:
    author_df.rename(columns={'designer_key': 'id',
                              'designer_name': 'name',
                              'designer_image_url': 'image_url',
                              'designer_url': 'url'
                              }, inplace=True)

    del author_df['designer_bga_id']
    del author_df['designer_bgg_key']
    del author_df['bgg_designer_name']

    upload_dataframe(author_df, 'games_author')

    # import users csv:
    author_relation_df = pd.read_csv(
        '../Data/Joined/Results/Designer_Game_Relation.csv',
        index_col=0,
        dtype={
            'game_key': int,
            'designer_key': int,
        })
    # rename a few columns:
    author_relation_df.rename(columns={'game_key': 'boardgame_id',
                                  'designer_key': 'author_id',
                                  }, inplace=True)

    upload_dataframe(author_relation_df, 'games_boardgame_author')


def upload_online_games_to_db():
    # import boardgame csv:
    board_game_df = pd.read_csv(
        '../Data/Joined/Integration',
        index_col=0)

    # rename a few columns:
    board_game_df.rename(columns={'game_key': 'id',
                                  'game_description': 'description',
                                  'min_players': 'min_number_of_players',
                                  'max_players': 'max_number_of_players',
                                  }, inplace=True)

    upload_dataframe(board_game_df, 'games_onlinegame')


def upload_similarboardonlinegame_to_db():
    # import boardgame csv:
    similar_df = pd.read_csv(
        '../Data/Joined/Integration',
        index_col=0)

    # rename a few columns:
    similar_df.rename(columns={'key': 'id'}, inplace=True)

    upload_dataframe(similar_df, 'games_boardgame')


def upload_dataframe(df: pd.DataFrame, table: str, batchsize: int = 1000):
    # create instance of Postgres Wrapper:
    dbWrapper = PostgresWrapper(host=os.getenv('POSTGRES_HOST_EXTERNAL'),
                                user=os.getenv('POSTGRES_USER'),
                                password=os.getenv('POSTGRES_PASSWORD'),
                                database=os.getenv('POSTGRES_DB'),
                                port=os.getenv('POSTGRES_PORT'))

    dbWrapper.connect()

    # execute upload
    dbWrapper.upload_dataframe(table=table,
                               df=df,
                               batchsize=batchsize,
                               truncate_table=True,
                               commit=True)

    logging.info('Upload completed')
    dbWrapper.disconnect()
    logging.info('Disconnected')
