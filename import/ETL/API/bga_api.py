import requests
from ratelimit import limits, sleep_and_retry
import math
import time
import pandas as pd
import numpy as np
from ETL.helper import export_dic_to_json, get_bga_ids_of_all_games, export_df_to_csv
from ETL.Cleaning.BoardGameAtlas.clean_boardgameatlas_data import get_ids_of_included_games
from datetime import datetime

##############################################################################################################
# Game API:
# https://api.boardgameatlas.com/api/search?client_id=16OTwjJZDB&ids=TAAifFP590,yqR4PtpO8X,RLlDWHh7hR
#
# Comment API:
# https://api.boardgameatlas.com/api/reviews?client_id=JLBr5npPhV&game_id=RLlDWHh7hR&skip=0&pretty=true
##############################################################################################################

# 30 calls per minute
CALLS = 30
RATE_LIMIT = 60

# wait 0.1 second before each API call
PAUSE_LENGTH = 0

# Batches:
BATCH_SIZE_GAME_INFO = 10000
BATCH_SIZE_REVIEWS = 200


def get_bga_game_information_from_api():
    # get list of all ids
    ids = get_bga_ids_of_all_games()

    # split ids in batches
    batch_size = BATCH_SIZE_GAME_INFO
    batches = split_into_batches(ids, batch_size)

    # loop over batch
    for i, batch in enumerate(batches):
        # get reviews for ids
        reviews = get_game_info_for_ids(batch)

        print('Batch ' + str(i + 1) + ' completed!' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))

        # save ids to json
        path = '../../Data/BoardGameAtlas/Raw/API/GameInformation/'
        export_dic_to_json(dic=reviews,
                           path_and_name=path + 'BgaGameInformationBatchNr_' + str(i + 1) + '-' + datetime.now().strftime(
                               "%d_%m_%Y-%H_%M") + '.json')


def get_game_info_for_ids(ids):
    url = 'https://api.boardgameatlas.com/api/search'

    # Split up batch again into smaller batches or "chunks"
    # Why? Because the number of game_ids in one BGA API request is limited to 100
    chunks = split_into_batches(list=ids, batchsize=100)

    batch_data = []

    for chunk in chunks:
        # join all ids from list to one long string of ids
        chunk_ids_as_str = ",".join(map(str, chunk))

        # set parameters for api call, especially ids
        params = {'pretty': 'true',
                  'client_id': '16OTwjJZDB',
                  'ids': chunk_ids_as_str
                  }

        # call api
        chunk_data = bga_api_call(url, params)
        chunk_data = chunk_data['games']

        # add data from chunk to batch
        batch_data = batch_data + chunk_data
    return batch_data


def bga_review_api_main():
    # get list of all ids
    ids = get_ids_of_included_games()

    # split ids in batches
    batch_size = BATCH_SIZE_REVIEWS
    batches = split_into_batches(ids, batch_size)

    # loop over batch
    for i, batch in enumerate(batches):
        # get reviews for ids
        reviews = get_bga_reviews(batch)

        print(datetime.now().strftime("%d_%m_%Y-%H_%M"))

        # save ids to json
        path = '../../Data/BoardGameAtlas/Raw/API/Reviews/'
        export_dic_to_json(reviews, path+'BgaGameReviewsBatchNr_' + str(i + 1) + '-' +
                           datetime.now().strftime("%d_%m_%Y-%H_%M") + '.json')


def get_bga_reviews(ids):
    url = 'https://api.boardgameatlas.com/api/reviews'
    params = {'pretty': 'true',
              'client_id': '16OTwjJZDB',
              'game_id': 'TAAifFP590',
              'skip': 0
              }

    data_list = {}

    for game_id in ids:
        skip_count = 0
        params['game_id'] = game_id
        params['skip'] = skip_count
        reviews_for_game = bga_api_call(url, params)
        temp = reviews_for_game

        while len(temp) == 100:
            skip_count += 100
            params['skip'] = skip_count
            temp = bga_api_call(url, params)
            reviews_for_game = reviews_for_game + temp

        data_list[str(game_id)] = reviews_for_game
        print('game_id ' + str(game_id) + ' completed ' + datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))

    return data_list


def get_bga_mechanics():
    url = 'https://api.boardgameatlas.com/api/game/mechanics?'
    params = {'client_id': '16OTwjJZDB'}

    # query API to get all mechanics
    mechanics = bga_api_call(url, params)['mechanics']

    # create mechanics dataframe
    mechanics_df = pd.DataFrame(mechanics)

    # drop checked column:
    del mechanics_df['checked']

    # rename a few columns
    mechanics_df.rename(columns={
        'id': 'mechanic_bga_id', 'name': 'mechanic_name', 'url': 'mechanic_bga_url'
    }, inplace=True)

    # export bga_mechanics:
    export_df_to_csv(mechanics_df, '../Data/BoardGameAtlas/Raw/API/Mechanics/all_bga_mechanics.csv')


def get_bga_categories():
    url = 'https://api.boardgameatlas.com/api/game/categories?'
    params = {'client_id': '16OTwjJZDB'}

    # query API to get all categories
    categories = bga_api_call(url, params)['categories']

    # create categories dataframe
    categories_df = pd.DataFrame(categories)

    # drop checked column:
    del categories_df['checked']

    # rename a few columns
    categories_df.rename(columns={
        'id': 'category_bga_id', 'name': 'category_name', 'url': 'category_bga_url'
    }, inplace=True)

    # export bga_categories:
    export_df_to_csv(categories_df, '../Data/BoardGameAtlas/Raw/API/Categories/all_bga_categories.csv')


def get_test_ids():
    ids = ['TAAifFP590', 'yqR4PtpO8X', 'RLlDWHh7hR', '5H5JS0KLzK', 'fDn9rQjH9O']
    return ids


def split_into_batches(list, batchsize):
    a = len(list)
    num_batches = math.ceil(len(list) / batchsize)

    batches = []
    for i in range(0, num_batches):
        temp = list[(i * batchsize):(min(((i + 1) * batchsize), len(list)))]
        batches.append(temp)

    return batches


def bga_api_call(url, params):
    time.sleep(PAUSE_LENGTH)
    check_limit()

    try:
        r = requests.get(url=url, params=params)
    except Exception:
        print("error in API call")
        print(Exception)

    data = r.json()

    # cut of reviews key since it is the only key which doesn't make much sense
    if "reviews" in data:
        data = data['reviews']

    # check if empty and recursively call function again (PROBLEM: what if there are exactly 100 reviews? -> skip=100 would be empty)
    # if not data:
    #    time.sleep(1)
    #    bga_api_call(url, params)

    # add additional delays in case of errors
    if "error" in data:
        if 'statusCode' in data['error'] and data['error']['statusCode'] == '429':
            print("Error: Rate limit for client_id is exceeded.")
            time.sleep(2)
            print("Sleep for 2 seconds")

    return data


# ensures that API is only called 60 times per minute
@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
def check_limit():
    """ Empty function just to check for calls to API """
    return
