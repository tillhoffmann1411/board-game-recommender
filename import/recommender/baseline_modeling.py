import numpy as np


def global_average_prediction(data):
    '''
    This function will take the prepared data and calculate the global average over all games and user and uses it as
    a prediction.
    '''

    #  get number of nonzero values (number of ratings)
    number_ratings = sum(data.count(axis=0))
    # get sum of all column sums
    sum_all_ratings = sum(data.sum(axis=0))
    # calculate global average
    global_average = sum_all_ratings / number_ratings
    print('---global average: ', global_average)

    # set 0 values to global average
    data[data.isna()] = global_average

    return data


def game_average_prediction(data):
    '''
    This function will take the prepared data and calculate the average for each game and uses it as a prediction
    for all user that have not rated the game.
    '''
    # count ratings per game column
    count_ratings = data.count(axis=0)
    # sum ratings per game column
    sum_ratings = data.sum(axis=0)

    # calculate game average
    game_average = sum_ratings / count_ratings
    # set average of NaN to 0
    game_average[np.isnan(game_average)] = 0
    print('---game average: ', game_average)

    # set game average for NaN
    data = data.fillna(game_average)

    return data


def user_average_prediction(data):
    '''
    This function will take the prepared data and calculate the average for each user and uses it as a prediction
    for all his unrated games.
    '''
    # count ratings per user column
    count_ratings = data.count(axis=1)
    # sum ratings per user column
    sum_ratings = data.sum(axis=1)

    # calculate user average
    user_average = sum_ratings / count_ratings
    # set average of NaN to 0
    user_average[np.isnan(user_average)] = 0
    print('---user average: ', user_average)
    # set user average for NaN
    data = data.T.fillna(user_average).T

    return data
