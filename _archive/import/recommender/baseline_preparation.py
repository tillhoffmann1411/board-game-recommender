import pandas as pd
import numpy as np
import random
import gc


def get_recommendation_data(link, min_number_ratings_game, min_number_ratings_user, size_user_sample, seed):
    """
    This function will load the reviews data and filter it for your needs.

    link: link to review data
    min_number_ratings_game: filter minimum number of ratings per game
    min_number_ratings_user: filter minimum number of ratings per user
    size_user_sample: number for sample size if you want to speed up the calculations
    seed: number if you want to compare your results, else None
     """

    # get data
    data = pd.read_csv(link, usecols=['user_key', 'game_key', 'rating'], sep=',', header=0)

    # filter games by number of reviews and sample x unique user form data
    # keep only games with more than x reviews
    num_reviews_game = data.loc[:, 'game_key'].value_counts()
    data = data[data.loc[:, 'game_key'].isin(num_reviews_game.index[num_reviews_game.gt(min_number_ratings_game)])]
    # keep only user with more than x reviews
    num_reviews_user = data.loc[:, 'user_key'].value_counts()
    data = data[data.loc[:, 'user_key'].isin(num_reviews_user.index[num_reviews_user.gt(min_number_ratings_user)])]
    # take only sample of users
    user_sample = pd.Series(data['user_key'].unique())
    user_sample = user_sample.sample(n=size_user_sample, replace=False, random_state=seed)
    user_sample = user_sample.tolist()
    data = data[data.user_key.isin(user_sample)]

    print('---data shape: ', data.shape)

    return data


def prepare_data(data):
    """
    This function will take the before loaded review data, prepare it and create the utility matrix.
    """

    # remove duplicates
    data = data.drop_duplicates(subset=['user_key', 'game_key'], keep='last')

    # create utility matrix
    data_pivot = data.pivot(index='user_key', columns='game_key', values='rating')

    # clean memory
    del data
    gc.collect()

    # info
    print('---pivot data shape: ', data_pivot.shape)

    return data_pivot


def make_train_test_split(data, test_size, seed):
    '''
    This function will split the data into train and test data for evaluation purposes. Therefore randomly x percentage
     of the known data points will be deleted and later used as test set to predict the performance of the model.
     Output will be a dict with the train data, original data and deleted positions for test purposes.

    data: utility matrix
    test_size: size of test set in percent
    seed: if you want to spilt data every time the same (for comparisons)
    '''

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

    # create dict for return
    d = {'train_data': train_data,
         'original_data': data,
         'delete_position': delete_position}

    return d


