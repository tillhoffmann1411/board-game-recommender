import pandas as pd
import numpy as np
from datetime import datetime
from ETL.helper import export_df_to_csv, export_df_to_pickle, export_df_to_parquet


def clean_bgg_games():
    filename = '../Data/BoardGameGeeks/Raw/games_detailed_info.csv'
    df = pd.read_csv(filename)

    # remove first column (unnamed):
    df.drop(df.columns[0], axis=1, inplace=True)

    # remove further unwanted columns:
    columns_to_remove = [
        'type',
        'playingtime',
        'boardgameartist',
        'boardgamefamily',
        'boardgameexpansion',
        'boardgameimplementation',
        'median',
        'owned',
        'wanting',
        'wishing',
        'trading',
        'numweights',
        'suggested_num_players',
        'suggested_playerage',
        'suggested_language_dependence',
        'boardgameintegration',
        'boardgamecompilation',
        'Strategy Game Rank',
        'Family Game Rank',
        'Party Game Rank',
        'Abstract Game Rank',
        'Thematic Rank',
        'War Game Rank',
        'Customizable Rank',
        "Children's Game Rank",
        'RPG Item Rank',
        'Accessory Rank',
        'Video Game Rank',
        'Amiga Rank',
        'Commodore 64 Rank',
        'Arcade Rank',
        'Atari ST Rank'
        ]
    df.drop(columns_to_remove, axis=1, inplace=True)


    # rename columns:
    df.rename(columns={
        'id': 'bgg_game_id',
        'primary': 'name',
        'yearpublished': 'year_published',
        'minplayers': 'min_players',
        'maxplayers': 'max_players',
        'minplaytime': 'min_playtime',
        'maxplaytime': 'max_playtime',
        'minage': 'min_age',
        'usersrated': 'bgg_num_user_ratings',
        'numcomments': 'bgg_num_user_comments',
        'average': 'bgg_average_user_rating',
        'bayesaverage': 'bgg_bayes_average',
        'stddev': 'bgg_stddev',
        'Board Game Rank': 'bgg_rank',
        'description': 'game_description',
        'image': 'image_url',
        'thumbnail': 'thumbnail_url',
        'averageweight': 'bgg_average_weight'
    }, inplace=True)

    # desired dataframes:
    # 1) main_game_information
    # 2) publishers
    # 3) designers
    # 4) mechanics
    # 5) categories
    # 6) names

    # 2) extract publishers from 'boardgamepublisher' column:
    # create subset dataframe with only id and names/alternate column:
    publishers_df = df[['bgg_game_id', 'boardgamepublisher']]

    # rename columns
    publishers_df.rename(columns={
        'bgg_game_id': 'bgg_game_id',
        'boardgamepublisher': 'publisher_name'
    }, inplace=True)

    # add empty column 'publisher_url' and 'publisher_id':
    publishers_df['publisher_url'] = np.nan
    publishers_df['publisher_id'] = np.nan

    # drop nas:
    publishers_df = publishers_df[publishers_df['publisher_name'].notna()]

    # lists are stored as strings and not as lists. Therefore we have to change the class from str to list:
    publishers_df['publisher_name'] = publishers_df['publisher_name'].apply(eval)

    # explode transforms each element of the list to a row
    publishers_df = publishers_df.explode('publisher_name')

    # drop column from games dataframe:
    del df['boardgamepublisher']

    # 3) extract designers from 'boardgamedesigner' column (sames procedure as for publishers)
    designers_df = df[['bgg_game_id', 'boardgamedesigner']]
    designers_df.rename(columns={'id': 'bgg_game_id', 'boardgamedesigner': 'designer_name'}, inplace=True)
    designers_df['designer_url'] = np.nan
    designers_df['designer_id'] = np.nan
    designers_df = designers_df[designers_df['designer_name'].notna()]
    designers_df['designer_name'] = designers_df['designer_name'].apply(eval)
    designers_df = designers_df.explode('designer_name')
    del df['boardgamedesigner']

    # 4) extract designers from 'boardgamemechanic' column
    mechanics_df = df[['bgg_game_id', 'boardgamemechanic']]
    mechanics_df.rename(columns={'id': 'bgg_game_id', 'boardgamemechanic': 'mechanic_name'}, inplace=True)
    mechanics_df['mechanic_id'] = np.nan
    mechanics_df['mechanic_url'] = np.nan
    mechanics_df = mechanics_df[mechanics_df['mechanic_name'].notna()]
    mechanics_df['mechanic_name'] = mechanics_df['mechanic_name'].apply(eval)
    mechanics_df = mechanics_df.explode('mechanic_name')
    del df['boardgamemechanic']

    # 5) extract designers from 'boardgamecategory' column
    categories_df = df[['bgg_game_id', 'boardgamecategory']]
    categories_df.rename(columns={'id': 'bgg_game_id', 'boardgamecategory': 'category_name'}, inplace=True)
    categories_df['category_id'] = np.nan
    categories_df['category_url'] = np.nan
    categories_df = categories_df[categories_df['category_name'].notna()]
    categories_df['category_name'] = categories_df['category_name'].apply(eval)
    categories_df = categories_df.explode('category_name')
    del df['boardgamecategory']

    # 6) extract names from 'alternate' column:
    names_df = df[['bgg_game_id', 'alternate']]
    names_df.rename(columns={'id': 'bgg_game_id', 'alternate': 'game_name'}, inplace=True)
    names_df = names_df[names_df['game_name'].notna()]
    names_df['game_name'] = names_df['game_name'].apply(eval)
    names_df = names_df.explode('game_name')
    del df['alternate']

    # Export all 6 dataframes:
    path = '../Data/BoardGameGeeks/Processed/GameInformation/'
    export_df_to_csv(df, path + '01_BGG_Game_Information_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.csv')
    export_df_to_csv(publishers_df, path + '02_BGG_Game_Publisher_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.csv')
    export_df_to_csv(designers_df, path + '03_BGG_Game_Designer_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.csv')
    export_df_to_csv(mechanics_df, path + '04_BGG_Game_Mechanic_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.csv')
    export_df_to_csv(categories_df, path + '05_BGG_Game_Category_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.csv')
    export_df_to_csv(names_df, path + '06_BGG_Game_Name_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.csv')


def clean_bgg_reviews():
    filename = '../Data/BoardGameGeeks/Raw/bgg-15m-reviews.csv'
    df = pd.read_csv(filename)

    # remove first column (unnamed):
    df.drop(df.columns[0], axis=1, inplace=True)

    # drop column name (game name is already indirectly included through the game_id)
    del df['name']

    # rename columns
    df.rename(columns={
        'user': 'user_name',
        'comment': 'review_text',
        'ID': 'game_id'
    }, inplace=True)

    # add column that states the origin of the comment (datasource)
    df['review_origin'] = 'bgg'

    # add column has_review_text (0 = only rating, no text; 1 = rating + text)
    df['has_review_text'] = np.where(df['review_text'].isnull(), 0, 1)

    # export dataframe to pickle:
    export_path = '../Data/BoardGameGeeks/Processed/Reviews/bgg_reviews_15m_CLEANED.pickle'
    export_df_to_pickle(df, export_path)


