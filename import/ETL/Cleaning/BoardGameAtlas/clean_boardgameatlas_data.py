import pandas as pd
import numpy as np
import os
import json
import glob
from datetime import datetime
from ETL.helper import import_json_to_dataframe, export_df_to_json, export_df_to_csv, \
    get_latest_version_of_file


def clean_bga_game_information_scraper():
    '''
    Function that cleans data collected by the BoardGameInfoSpider.
    Dataframe is then saved to a JSON file.
    '''

    df = import_json_to_dataframe('../Data/BoardGameAtlas/Raw/Scrapy/BoardGameInformationScraper.json')

    # remove unwanted symbols (especially brackets)
    unwanted_symbols = ['[', ']', "'"]
    for col in df.columns:
        df[col] = df[col].astype(str)
        for symbol in unwanted_symbols:
            df[col] = df[col].str.replace(symbol, '')

    # remove white spaces at beginning and end of strings
    df.columns = df.columns.str.strip()

    # clean gameID "game-foRKR22fGQ" -> "foRKR22fGQ"
    df['bga_game_id'] = df['bga_game_id'].str.split('game-').str[1]

    # remove "Rank:" from rank: "Rank: 1" -> "1"
    df['rank'] = df['rank'].str.replace("Rank:", '')

    # split num_players_and_play_time
    num_players_and_play_time = df.num_players_and_play_time.str.split(",", expand=True, )
    df[['num_players', 'play_time']] = num_players_and_play_time
    df.drop('num_players_and_play_time', axis=1, inplace=True)

    # remove all duplicates
    print('Number of duplicates removed: ' + str(len(df) - len(df.drop_duplicates(subset='bga_game_id', keep="first"))))
    df = df.drop_duplicates(subset='bga_game_id', keep="first")

    # create json file
    export_df_to_json(df,'../Data/BoardGameAtlas/Processed/bga_GameInformation_scrapy_Cleaned.json')


def create_list_of_ids_of_all_bga_games():
    print(os.getcwd())
    # import data scraped by GameInformation Spider
    df = pd.read_json('../Data/BoardGameAtlas/Processed/Scrapy/bga_GameInformation_scrapy_CLEANED.json')

    # Extract Ids
    df = df[['bga_game_id']]
    ids = df['bga_game_id'].tolist()

    # Store ids as Json
    export_df_to_json(df, '../Data/BoardGameAtlas/Processed/Scrapy/bga_all_120k_game_ids.json')


def bga_get_num_ratings_per_game():
    '''
    Function puts together the results from GameInfo API calls which where a stored in one JSON file per batch.
    In a second step, only the gameId, name and num_user_ratings are extracted. These three columns for all 120,000 bga
    games is then stored in a separate json file.
    '''
    # get list of filenames:
    path = '../Data/BoardGameAtlas/Raw/API/GameInformation'
    filenames = []

    for r, d, f in os.walk(path):
        for file in f:
            if '.json' in file:
                filenames.append(os.path.join(r, file))

    # import data from filenames
    content = []

    for filename in filenames:
        with open(filename) as bga_json:
            read_file_content = json.load(bga_json)
            content = content + read_file_content

    # extract id, name, num_user_ratings
    ids = []
    names = []
    num_user_ratings = []

    for game in content:
        id = game['id']
        name = game['name']
        count = game['num_user_ratings']
        ids.append(id)
        names.append(name)
        num_user_ratings.append(count)

    # combine all back to one dictionary
    content_dictionary = {'id': ids, 'name': names, 'num_user_ratings': num_user_ratings}

    # dictionary to dataframe
    df = pd.DataFrame(content_dictionary)
    output_path = '../Data/BoardGameAtlas/Processed/API'
    export_df_to_json(df, output_path + '/bga_all_games_ids_names_numRatings.json')


def create_json_with_games_that_fulfill_ratings_amount():
    '''
    Creates a small json that only includes information on games with a certain amount of user_ratings.
    Information is GameID, Name and num_user_ratings.
    '''
    filename = '../Data/BoardGameAtlas/Processed/API/bga_all_games_ids_names_numRatings.json'
    df = import_json_to_dataframe(filename)

    # cut of games that have less ratings than 3:
    # results in 8246 games and 162,045 reviews for these games. This is equal to 91.26% of all user ratings.
    max_amount_ratings = 999999
    min_amount_ratings = 3
    df = df[df.num_user_ratings >= min_amount_ratings].reset_index(drop=True).sort_values(by=['num_user_ratings'],
                                                                                          ascending=False)
    df = df[df.num_user_ratings <= max_amount_ratings].reset_index(drop=True).sort_values(by=['num_user_ratings'],
                                                                                          ascending=False)

    # export games:
    filename_export = '../Data/BoardGameAtlas/Processed/API/bga_games_with_more_or_equal_3_reviews.json'
    export_df_to_json(df, filename_export)


def gather_bga_api_review_data():
    # get subfolders in which JSON files are stored
    path = '../Data/BoardGameAtlas/Raw/API/Reviews'
    subfolders = [f.path for f in os.scandir(path) if f.is_dir()]

    df_list_subfolders = []

    for subfolder in subfolders:
        # get all JSON files in that subfolder
        filenames = []
        for r, d, f in os.walk(path):
            for file in f:
                if '.json' in file:
                    filenames.append(os.path.join(r, file))

        # import json data from these files
        reviews = {}
        for filename in filenames:
            with open(filename) as bga_json:
                file_content = json.load(bga_json)
                reviews.update(file_content)

        # remove games key as it is already contained in key
        for game in reviews.items():
            for review in game[1]:
                del review['game']

        df_list = []
        for game in reviews.items():
            temp_df = pd.json_normalize(game[1])
            temp_df['game_id'] = game[0]

            # Creating a list of dataframes and then concatenating them all at once at the end is is way faster!
            df_list.append(temp_df)

        # Concat the dataframes in the previously created list to one big dataframe.
        df_subfolders = pd.concat(df_list, ignore_index=True, sort=False)
        df_list_subfolders.append(df_subfolders)

    # concat the dataframes for each folder
    df = pd.concat(df_list_subfolders, ignore_index=True, sort=False)

    # rename a few columns
    df.rename(columns={
        'id': 'review_id', 'user.username': 'username', 'user.id': 'user_id', 'description': 'review_text',
        'title': 'review_title'
    }, inplace=True)

    # count duplicates
    print('Number of duplicates (abs): ' + str(len(df) - len(df.drop_duplicates())))
    print('Number of duplicates (rel): ' + str(1 - len(df.drop_duplicates()) / len(df)) + ' %')

    # drop duplicates
    df.drop_duplicates(inplace=True)

    # export df to json:
    export_path = '../Data/BoardGameAtlas/Processed/API/bga_all_reviews_for_games_with_more_than_2_reviews.json'
    export_df_to_json(df, export_path)


def clean_bga_api_review_data():

    filename = '../Data/BoardGameAtlas/Processed/API/bga_all_reviews_for_games_with_more_than_2_reviews.json'
    # first check if file already exists:
    # if file doesn't exist call function to create it:
    if not os.path.isfile(filename):
        gather_bga_api_review_data()

    # import data
    df = import_json_to_dataframe('../Data/BoardGameAtlas/Processed/API/bga_all_reviews_for_games_with_more_than_2_reviews.json')

    # double the ratings columns to adjust the scale
    df['rating'] *= 2

    # drop column review_title
    del df['review_title']

    # add column has_review_text (0 = only rating, no text; 1 = rating + text)
    df['has_review_text'] = np.where(df['review_text'].isnull(), 0, 1)

    # add column that states the origin of the comment (datasource)
    df['review_origin'] = 'bga'

    # rename columns:
    df.rename(columns={
        'username': 'user_name',
        'date': 'review_date'
    }, inplace=True)

    export_df_to_csv(df, '../Data/BoardGameAtlas/Processed/API/bga_all_reviews_for_games_with_more_than_2_reviews_CLEANED.csv')


def gather_bga_api_game_information():
    '''
    Function puts together the results from GameInfo API calls which a stored in one JSON file per batch and
    then saves the data to a JSON file and returns it.
    '''

    # get list of filenames:
    path = '../Data/BoardGameAtlas/Raw/API/GameInformation'
    filenames = []

    for r, d, f in os.walk(path):
        for file in f:
            if '.json' in file:
                filenames.append(os.path.join(r, file))

    # import data from filenames
    content = []

    for filename in filenames:
        with open(filename) as bga_json:
            read_file_content = json.load(bga_json)
            content = content + read_file_content

    # export data to json file
    with open('../Data/BoardGameAtlas/Processed/API/BgaGameInformation_all_120000_games.json', 'w') as fp:
        json.dump(content, fp, sort_keys=False, indent=4)
        fp.close()


def clean_bga_api_game_information():

    # check if file already exists:
    filename = '../Data/BoardGameAtlas/Processed/API/BgaGameInformation_all_120000_games.json'

    if os.path.isfile(filename):
        # if it exists the merge step can be skipped
        pass
    else:
        # if not merge game_information batches into large json file containing all information
        gather_bga_api_game_information()

    # import data
    with open(filename) as bga_json:
        data = json.load(bga_json)
        bga_json.close()

    # remove games with < 3 reviews
    data = [game for game in data if game['num_user_ratings'] >= 3]

    # remove unwanted keys:
    entries_to_remove = [
        'images', 'msrps', 'discount', 'developers', 'artists',
        'weight_amount', 'weight_units', 'size_height', 'size_depth', 'size_units', 'size_width',
        'matches_specs', 'specs', 'spec', 'description', 'rules_url']
    for game in data:
        for key in entries_to_remove:
            game.pop(key, None)

    # desired dataframes:
    # 1) main_game_information
    # 2) publishers
    # 3) designers
    # 4) mechanics
    # 5) categories
    # 6) names

    # 2) Publishers
    publishers_list = []
    for game in data:
        for publisher in game['publishers']:
            publisher_dic = {'game_id': game['id'], 'publisher_id': publisher['id'], 'publisher_url': publisher['url']}
            publishers_list.append(publisher_dic)
    # build dataframe from extracted data:
    publishers_df = pd.DataFrame.from_dict(publishers_list)

    # 3) Designers / Authors
    # extract designers:
    designers_list = []
    for game in data:
        for designer in game['designers']:
            designer_dic = {'game_id': game['id'], 'designer_id': designer['id'],
                            'designer_url': designer['url']}
            designers_list.append(designer_dic)
    # build dataframe from extracted data:
    designers_df = pd.DataFrame.from_dict(designers_list)

    # 4) Mechanics
    # extract mechanics:
    mechanics_list = []
    for game in data:
        for mechanic in game['mechanics']:
            mechanic_dic = {'game_id': game['id'], 'mechanic_id': mechanic['id']}
            mechanics_list.append(mechanic_dic)
    # build dataframe from extracted data:
    mechanics_df = pd.DataFrame.from_dict(mechanics_list)

    # 5) categories
    # extract categories:
    categories_list = []
    for game in data:
        for category in game['categories']:
            category_dic = {'game_id': game['id'], 'category_id': category['id']}
            categories_list.append(category_dic)
    # build dataframe from extracted data:
    categories_df = pd.DataFrame.from_dict(categories_list)

    # 6) names
    # extract names:
    names_list = []
    for game in data:
        for name in game['names']:
            name_dic = {'game_id': game['id'], 'game_name': name}
            names_list.append(name_dic)
    # build dataframe from extracted data:
    names_df = pd.DataFrame.from_dict(names_list)

    # remove publishers, designers, mechanics, categories, names from games_list
    entries_to_remove = ['publishers', 'mechanics', 'categories', 'designers', 'names']
    for game in data:
        for key in entries_to_remove:
            game.pop(key, None)

    # add primary designers (only name) to games_list and remove dictionary primary designer
    for game in data:
        if 'primary_designer' in game:
            if 'name' in game['primary_designer']:
                game['main_designer_name'] = game['primary_designer']['name']
                game['main_designer_id'] = game['primary_designer']['id']
                game['main_designer_url'] = game['primary_designer']['url']
        game.pop('primary_designer', None)

    # do the same for primary publisher
    for game in data:
        if 'primary_publisher' in game:
            if 'name' in game['primary_publisher']:
                game['main_publisher_name'] = game['primary_publisher']['name']
                game['main_publisher_id'] = game['primary_publisher']['id']
                game['main_publisher_url'] = game['primary_publisher']['url']
        game.pop('primary_publisher', None)

    # 1) main game information
    # create dataframe:
    game_information_df = pd.DataFrame.from_dict(data)

    # rename a few columns:
    game_information_df.rename(columns={
        'id': 'bga_game_id',
        'num_user_ratings': 'bga_num_user_ratings',
        'average_user_rating': 'bga_average_user_rating',
        'rank': 'bga_rank',
        'trending_rank': 'bga_trending_rank',
        'description_preview': 'game_description',
        'thumb_url': 'thumbnail_url',
        'url': 'bga_game_url',
        'price': 'bga_price_us_dollar'
    }, inplace=True)

    # double the avg rating scores so they fit the bgg rating scale:
    game_information_df['bga_average_user_rating'] *= 2

    # Export all 6 dataframes:
    path = '../Data/BoardGameAtlas/Processed/API/'
    export_df_to_json(game_information_df, path+'01_BGA_Game_Information_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.json')
    export_df_to_json(publishers_df, path+'02_BGA_Game_Publishers_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.json')
    export_df_to_json(designers_df, path+'03_BGA_Game_Designers_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.json')
    export_df_to_json(mechanics_df, path+'04_BGA_Game_Mechanics_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.json')
    export_df_to_json(categories_df, path+'05_BGA_Game_Categories_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.json')
    export_df_to_json(names_df, path+'06_BGA_Game_Names_Relation_' + datetime.now().strftime("%d_%m_%Y-%H_%M") + '.json')



def create_id_list_of_included_bga_games():
    """
    Extracts ids of bga games previously obtained from bga api and create a JSON file containing the IDs.
    This list will later be used for the BGA Review API requests.
    """

    # import file that contains information on bga_games
    # since the exact filename is unknown, we have to find file and its latest version first:
    filename = get_latest_version_of_file('../Data/BoardGameAtlas/Processed/API/01_BGA_Game_Information_*.json')

    data = import_json_to_dataframe(filename)

    # extract ids
    ids = data['bga_game_id']

    # export data to json file
    filename_export = '../Data/BoardGameAtlas/Processed/API/BGA_Ids_of_boardgames_included.json'
    export_df_to_json(ids, filename_export)


def get_ids_of_included_games():
    # check if file already exists:
    filename = '../Data/BoardGameAtlas/Processed/API/BGA_Ids_of_boardgames_included.json'

    # if file doesn't exist call function to create it:
    if not os.path.isfile(filename):
        create_id_list_of_included_bga_games()

    # import data
    ids_df = import_json_to_dataframe(filename)
    ids_list = ids_df.iloc[:, 0].tolist()

    return ids_list
