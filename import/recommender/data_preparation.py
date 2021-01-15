import pandas as pd
import numpy as np
import random
from scipy.sparse import csr_matrix
import gc


def get_recommendation_data(link, sample_number_rows, random_state):
    """ output:     pandas data frame """
    # get data
    data = pd.read_csv(link, usecols=['user_key', 'game_key', 'rating'], sep=',', header=0)

    # randomly select n rows
    data_sample = data.sample(n=sample_number_rows, random_state=random_state)
    del data
    gc.collect()

    print('---data shape: ', data_sample.shape)

    return data_sample


def prepare_data(data, min_number_ratings_user=0, min_number_ratings_game=0):
    """ output:     pandas data frame - utility matrix """
    # remove duplicates
    data = data.drop_duplicates(subset=['user_key', 'game_key'], keep='last')

    # create utility matrix
    data_pivot = data.pivot(index='user_key', columns='game_key', values='rating')
    #data_pivot = create_matrix(data=data, user_col='user_key', item_col='game_key', rating_col='rating')
    #test = pd.DataFrame.sparse.from_spmatrix(data_pivot)

    ## filter user and games with only few ratings
    # count non zero values per game and user
    non_zero_games = data_pivot.count(axis=0)
    non_zero_user = data_pivot.count(axis=1)
    # create boolean arrays for filter
    non_zero_user_boolean = non_zero_user >= min_number_ratings_user
    non_zero_games_boolean = non_zero_games >= min_number_ratings_game
    # filter data
    data_pivot = data_pivot.loc[non_zero_user_boolean, non_zero_games_boolean]

    # info
    print('---pivot data shape: ', data_pivot.shape)
    # calculate sparsity of matrix
    print('---sparsity of matrix', len(data) / (len(data)*len(data.columns))) # if sparsity < 0.005 -> collaborative filtering might not be best option

    return data_pivot


def make_train_test_split(data, train_size, test_size, seed):
    # save position (index, column) for all ratings higher 0
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
    print("---deleted positions: ", round(n_row_test))

    # create train set - delete randomly chosen positions
    train_data = data.copy()
    for index, col in delete_position:
        train_data.loc[index, col] = np.NaN

    # create test set?
    # do i need a test set or is it enough if i return the positions to compare (deleted positions) later to calculate rmse?

    # create dict for return
    d = {'train_data': train_data,
         'original_data': data,
         'delete_position': delete_position}

    return d


def create_matrix(data, user_col, item_col, rating_col):
    """
    creates the sparse user-item interaction matrix

    Parameters
    ----------
    data : DataFrame
        implicit rating data

    user_col : str
        user column name

    item_col : str
        item column name

    ratings_col : str
        implicit rating column name
    """

    # create a sparse matrix of using the (rating, (rows, cols)) format
    rows = data[user_col].astype('category').cat.codes
    cols = data[item_col].astype('category').cat.codes
    rating = data[rating_col]
    ratings = csr_matrix((rating, (rows, cols)))
    ratings.eliminate_zeros()
    return ratings, data
