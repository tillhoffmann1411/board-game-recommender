import pandas as pd
import numpy as np
import random


def get_recommendation_data(link, sample_number_rows, random_state):
    """ output:     pandas data frame """
    # get data
    data = pd.read_csv(link, sep=',', header=0)

    # randomly select n rows
    data_sample = data.sample(n=sample_number_rows, random_state=random_state)
    print('---data shape: ', data_sample.shape)

    return data_sample


def prepare_data(data, min_number_ratings_user=0, min_number_ratings_game=0, fill=0):
    """ output:     pandas data frame - utility matrix """
    # create utility matrix
    data_pivot = data.pivot(index='user_key', columns='game_key', values='rating').fillna(fill)  # zero means worst possible rating

    ## filter user and games with only few ratings
    # count non zero values per game and user
    non_zero_games = np.count_nonzero(data_pivot, axis=0)
    non_zero_user = np.count_nonzero(data_pivot, axis=1)
    # create boolean arrays
    non_zero_user_boolean = non_zero_user >= min_number_ratings_user
    non_zero_games_boolean = non_zero_games >= min_number_ratings_game
    # filter data
    data_pivot = data_pivot.loc[non_zero_user_boolean, non_zero_games_boolean]

    # info
    print('---pivot data shape: ', data.shape)
    # calculate sparsity of matrix
    print('---sparsity of matrix', len(data) / (len(data)*len(data.columns))) # if sparsity < 0.005 -> collaborative filtering might not be best option

    return data_pivot


def make_train_test_split(data, train_size, test_size, seed):
    # save position (index, column) for all ratings higher 0
    i = 0
    position = []
    for col in data.columns:
        index = data.index[data.loc[:, col] > 0].tolist()
        # save every index on index list
        for elem in index:
            position.append((elem, col))

    # randomly choose elements from position tuple
    n_row_test = len(position)*test_size
    random.seed(seed)
    delete_position = random.sample(position, k=round(n_row_test))
    print("---test set: ", n_row_test)

    # create train set - delete randomly chosen positions
    train_data = data.copy()
    for index, col in delete_position:
        train_data.loc[index, col] = 0

    # create test set?
    # do i need a test set or is it enough if i return the positions to compare (deleted positions) later to calculate rmse?

    # create dict for return
    d = {'train_data': train_data,
         'delete_position': delete_position}

    return d
