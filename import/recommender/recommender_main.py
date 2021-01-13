
# Questions Monday:
# - what approaches should we try?
# - how many approaches should we try?
# - is this true: first step - measure similarity of user, second step - calculate prediction based on similar users

# Questions Group:


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import sys
import time


def get_recommendation_data(link, sample_number_rows):
    """ output:     pandas data frame """

    data = pd.read_csv(link, sep=',', header=0, nrows=sample_number_rows)
    print('---data shape: ', data.shape)

    # filter in sql query - only get data from users when they are also rated at least one same game with new_user
    return data


def prepare_data(data):
    # create utility matrix
    data_pivot = data.pivot(index='user', columns='name', values='rating').fillna(0)  # zero means worst possible rating

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
    print('sparsity of matrix', len(data) / (len(data)*len(data.columns))) # if sparsity < 0.005 -> collaborative filtering might not be best option

    return data_pivot


def make_train_test_split(data, train_size, test_size, random_state):
    # split data
    train_data, test_data = train_test_split(data, test_size=test_size, train_size=train_size, random_state=42)

    # select all user with more than 2 ratings
    # copy() data
    # delete

    return [train, test]


def get_cosine_similarity(x, y):
    numerator = np.dot(x, y)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)

    # a and b must be non-zero vectors
    if denominator > 0:
        sim = numerator / denominator
    else:
        sim = 0

    return sim


# does not work here - assumption to added zero ratings for unrated games leads to wrong results
def calculate_similarity(data, new_user, method):
    # get items of requested user
    item_requested = data.loc[new_user].to_numpy()
    position_requested_user = list(data.index).index(new_user)
    print("-----item_requested: ", item_requested, "index number: ", position_requested_user)

    if method == 'cosine_similarity':
        print('..use cosine_similarity')
    elif method == 'centered_cosine_similarity':
        print('..use centered_cosine_similarity')
        # calculate mean per user - use only nonzero values
        mean_user = data.sum(axis=1) / data.apply(np.count_nonzero, axis=1)
        # replace nan and inf with 0 rating
        mean_user = mean_user.replace([np.inf, -np.inf], np.nan).fillna(value=0)

        # subtract mean only from nonzero values
        data = data.sub(mean_user, axis=0).multiply(data > 0).add(0)

    # create empty list to collect results
    similarities = []

    # compute similarity for all user
    for i in range(len(data.index)):
        if i != position_requested_user:
            # get item_to_compare
            item_to_compare = data.iloc[i].to_numpy()
            print("------item_to_compare: ", item_to_compare)

            # compare both items (item_requested and item_to_compare)
            sim = get_cosine_similarity(x=item_requested, y=item_to_compare)
            similarities.append((i, sim))

    # sort results
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    print(sorted_similarities)

    return [sorted_similarities, item_requested]


def calculate_baseline(data, item_requested, method, threshold_min_number_ratings_per_game):
    if method == 'average':
        # calculate average rating for each game
        numerator = data.apply(np.sum, axis=0)
        denominator = data.apply(np.count_nonzero, axis=0)

        # set denominator 0 if less than x reviews (otherwise games biased)
        denominator = [elem if elem >= threshold_min_number_ratings_per_game else 0 for elem in denominator]
        # calculate baseline
        baseline = numerator / denominator
        # replace nan and inf with 0 rating
        baseline = baseline.replace([np.inf, -np.inf], np.nan).fillna(value=0)

        # delete games new_user rated already
        item_requested_boolean = [not bool(x) for x in item_requested]
        # select only games user has not rated
        baseline = baseline[item_requested_boolean]

        return baseline


def prepare_prediction_data(data, item_requested, similarities, threshold_filter_similar_user):
    # filter group of most similar user
    similar_users = list(filter(lambda x: x[1] >= threshold_filter_similar_user, similarities))
    similar_users = [i[0] for i in similar_users]
    data_prediction = data.iloc[similar_users]

    # create data frame with games user has not rated yet, delete games user rated already
    item_requested_boolean = [not bool(x) for x in item_requested]
    # select only games user has not rated
    data_prediction = data_prediction.loc[:, item_requested_boolean]

    return data_prediction


def predict(data, baseline, threshold_min_number_ratings_per_game):
    # sum ratings per game
    numerator = data.apply(np.sum, axis=0)
    # count number of ratings
    denominator = data.apply(np.count_nonzero, axis=0)
    # if less than threshold ratings give game rating if 0
    denominator_prepared = [elem if elem >= threshold_min_number_ratings_per_game else 0 for elem in denominator]
    # calculate prediction
    pred_similar_users = numerator / denominator_prepared
    # clean prediction
    pred_similar_users = pred_similar_users.replace([np.inf, -np.inf], np.nan).fillna(value=0)

    # use baseline for all games without proper review
    pred = pred_similar_users.combine(baseline, lambda x, y: y if x == 0 else x)

    # sort and add information to table
    pred_info = pd.concat([pred, denominator, numerator], axis=1)
    pred_info = pred_info.sort_values(by=[0, 1], ascending=False)

    # sort predictions
    sorted_pred = pred_info.iloc[:, 0]

    return [sorted_pred, pred_info]


def calculate_global_average(data):
    calculation_data = data.replace(0, np.NaN)
    global_average = calculation_data.mean()

    print('--- global mean: ', global_average)
    return global_average


if __name__ == "__main__":
    # get data from database
    df = get_recommendation_data(link='../Data/test_data/test_2mil.csv',
                                 sample_number_rows=5000)

    # get new user name for recommendation
    new_user = "Artax"  #"4Corners"  # from frontend?

    # prepare data
    df = prepare_data(data=df,
                      min_number_ratings_user=0,
                      min_number_ratings_game=0)

    # split data
    train_data, test_data = train_test_split(df,
                                             test_size=0.8,
                                             train_size=0.2,
                                             random_state=42)

    # calculate user similarities
    result_similarity = calculate_similarity(data=df,
                                             new_user=new_user,
                                             method="centered_cosine_similarity")

    # calculate baseline rating
    baseline = calculate_baseline(data=df,
                                  item_requested=result_similarity[1],
                                  method="average",
                                  threshold_min_number_ratings_per_game=20)

    # prepare data for prediction
    prediction_data = prepare_prediction_data(data=df,
                                              item_requested=result_similarity[1],
                                              similarities=result_similarity[0],
                                              threshold_filter_similar_user=0.2)

    # predict (can also use other models) - average rating in user group
    prediction = predict(data=prediction_data,
                         baseline=baseline,
                         threshold_min_number_ratings_per_game=2)

    print(prediction[1])
    prediction[1].to_csv(path_or_buf='/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data/pred_res_info.csv')

