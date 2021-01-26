# get similar games
import pandas as pd
import numpy as np
import gc

from pandas.core.frame import DataFrame


def get_recommendation_data(data, min_number_ratings_game, min_number_ratings_user, size_user_sample, seed):
    """ output:     pandas data frame """
    # get data
    # data = pd.read_csv(link, usecols=['created_by_id', 'game_id', 'rating'], sep=',', header=0)

    # filter games by number of reviews and sample x unique user form data
    # keep only games with more than x reviews
    # print('Num Reviews: ' + str(len(data)))
    num_reviews_game = data.loc[:, 'game_id'].value_counts()
    data = data[data.loc[:, 'game_id'].isin(num_reviews_game.index[num_reviews_game.gt(min_number_ratings_game)])]
    # keep only user with more than x reviews
    num_reviews_user = data.loc[:, 'created_by_id'].value_counts()
    data = data[data.loc[:, 'created_by_id'].isin(num_reviews_user.index[num_reviews_user.gt(min_number_ratings_user)])]
    # take only sample of users
    user_sample = pd.Series(data['created_by_id'].unique())
    # user_sample = user_sample.sample(n=size_user_sample, replace=False, random_state=seed)
    user_sample = user_sample.tolist()
    data = data[data.created_by_id.isin(user_sample)]

    # print('---data shape: ', data.shape)

    return data


def prepare_data(data):
    """ output:     pandas data frame - utility matrix """
    # remove duplicates
    data = data.drop_duplicates(subset=['created_by_id', 'game_id'], keep='last')

    # create utility matrix
    data_pivot = data.pivot(index='created_by_id', columns='game_id', values='rating')

    # clean memory
    del data
    gc.collect()

    # info
    # print('---pivot data shape: ', data_pivot.shape)

    return data_pivot


def calculate_centered_cosine_similarity(data, new_user):

    # calculate mean per user
    mean_user = data.mean(axis=1)
    # subtract mean only from nonzero values
    data = data.sub(mean_user, axis=0)
    # fill nan with 0
    data = data.fillna(0)

    # get items of requested user
    item_requested = data.loc[new_user].to_numpy()
    position_requested_user = list(data.index).index(new_user)
    # print("-----item_requested: ", item_requested, "index number: ", position_requested_user)

    # create empty list to collect results
    similarities = []

    # compute similarity for all user
    for i in range(len(data.index)):
        if i != position_requested_user:
            # get item_to_compare
            item_to_compare = data.iloc[i].to_numpy()
            # print("------item_to_compare: ", item_to_compare)

            # compare both items (item_requested and item_to_compare)
            sim = get_cosine_similarity(x=item_requested, y=item_to_compare)
            similarities.append((i, sim))

    # sort results
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    # print(sorted_similarities)

    return [sorted_similarities, item_requested]


def get_cosine_similarity(x, y):
    numerator = np.dot(x, y)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)

    # a and b must be non-zero vectors
    if denominator > 0:
        sim = numerator / denominator
    else:
        sim = 0

    return sim


def prepare_prediction_data(data, item_requested, similarities, threshold_compare_best_n_percentage):
    # take best x percent of user for prediction
    number_sim_user = round(len(similarities) * threshold_compare_best_n_percentage)
    similar_users = similarities[:number_sim_user]

    # filter group of most similar user
    similar_users = [i[0] for i in similar_users]
    data_prediction = data.iloc[similar_users]

    # create data frame with games user has not rated yet, delete games user rated already
    item_requested_boolean = [not bool(x) for x in item_requested]
    # select only games user has not rated
    data_prediction = data_prediction.loc[:, item_requested_boolean]

    return data_prediction


def predict(data, threshold_min_number_ratings_per_game):
    # sum ratings per game
    numerator = data.sum(axis=0)
    # count number of ratings
    denominator = data.count(axis=0)
    # if less than threshold ratings give game rating if 0
    denominator_prepared = [elem if elem >= threshold_min_number_ratings_per_game else 0 for elem in denominator]
    # calculate prediction
    pred = numerator / denominator_prepared
    # clean prediction
    pred = pred.replace([np.inf, -np.inf], np.nan).fillna(value=0)

    # sort and add information to table
    pred_info = pd.concat([pred, denominator, numerator], axis=1)
    pred_info = pred_info.sort_values(by=[0, 1], ascending=False)

    # sort predictions
    sorted_pred = pred_info.iloc[:, 0]

    return [sorted_pred, pred_info]


def main():
    # get user id - frontend
    user_id = 4

    # get all data to compare
    data = get_recommendation_data(link='./Reviews.csv',
                                   min_number_ratings_game=500,
                                   min_number_ratings_user=10,
                                   size_user_sample=5_000,
                                   seed=2352)  # if None random games

    # create utility matrix
    data = prepare_data(data=data)

    # calculate user similarities
    result_similarity, item_requested = calculate_centered_cosine_similarity(data=data,
                                                                             new_user=user_id)
    # create most similar user group
    data = prepare_prediction_data(data=data,
                                   item_requested=item_requested,
                                   similarities=result_similarity,
                                   threshold_compare_best_n_percentage=0.2)

    # get average game rating from similar users
    sorted_pred, pred_info = predict(data,
                                     threshold_min_number_ratings_per_game=50)

    # print('info about game predictions: \t', pred_info)

    # send sorted_pred to frontend


if __name__ == '__main__':
    main()
