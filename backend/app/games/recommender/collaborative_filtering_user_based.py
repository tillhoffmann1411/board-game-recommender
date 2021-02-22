import pandas as pd
import numpy as np
import gc
from pandas.core.frame import DataFrame


def get_recommendation_data(data, min_number_ratings_game):
    """
    function will filter data and make sure that no games with less than min_number_ratings_game are in data. Output
    will be a filtered pandas data frame.

    data:                       data from data base
    min_number_ratings_game:    number which states how many reviews a game should have at least
    """

    # filter games by number of reviews and sample x unique user form data
    # keep only games with more than x reviews
    num_reviews_game = data.loc[:, 'game_key'].value_counts()
    data = data[data.loc[:, 'game_key'].isin(num_reviews_game.index[num_reviews_game.gt(min_number_ratings_game)])]
    return data


def prepare_data(data):
    """
    function will prepare the from the data base and create the utility matrix. Output will be the utility matrix as
    pandas data frame.
    """
    # remove duplicates
    data = data.drop_duplicates(subset=['created_by_id', 'game_key'], keep='last')

    # create utility matrix
    data_pivot = data.pivot(index='created_by_id', columns='game_key', values='rating')

    # clean memory
    del data
    gc.collect()

    return data_pivot


def calculate_centered_cosine_similarity(data, new_user):
    '''
    function will calculate the centered cosine similarity between the ratings of the new_user and all other users.
    Output is a sorted list of tuples with similarity scores between the new_user and all other users and the
    information of items of requested user.

    data:       utility matrix data
    new_user:   user_id of user in frontend
    '''

    # prepare for centered cosine similarity
    # calculate mean per user
    mean_user = data.mean(axis=1)
    # subtract mean only from nonzero values
    data = data.sub(mean_user, axis=0)
    # fill nan with 0
    data = data.fillna(0)

    # get items of requested user
    item_requested = data.loc[new_user].to_numpy()
    position_requested_user = list(data.index).index(new_user)

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

    return [sorted_similarities, item_requested]


def get_cosine_similarity(x, y):
    '''
    function will calculate the cosine similarity between two arrays x and y.

    x:  array with item ratings of frontend user
    y:  array with item ratings of other user to compare
    '''

    numerator = np.dot(x, y)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)

    # a and b must be non-zero vectors
    if denominator > 0:
        sim = numerator / denominator
    else:
        sim = 0

    return sim


def prepare_prediction_data(data, item_requested, similarities, threshold_compare_best_n_percentage):
    '''
    function will create a group of most similar users to the frontend user. This group os later used to predict games
    which might the frontend user also like.

    data:                                   utility matrix data
    item_requested:                         item ratings of frontend user
    similarities:                           array with calculated similarities
    threshold_compare_best_n_percentage:    threshold for creating the similar user group, defines size of group by
                                            percentage over all users
    '''

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
    '''
    function will calculate the mean rating of each game in the most similar user group. The games with the highest
    average rating will be used as prediction if they have more than threshold_min_number_ratings_per_game ratings per
    game.

    data:                                   group of most similar user
    threshold_min_number_ratings_per_game:  number which states how many rataings a game should have in the similar user
                                            group
    '''

    # sum ratings per game
    numerator = data.sum(axis=0)
    # count number of ratings
    denominator = data.count(axis=0)
    # if less than threshold ratings give game rating of 0
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


def similiar_users(user_id: int, data: pd.DataFrame, num_recommendations: int = 50):
    '''
    collaborative filtering approach on user basis:
    this function is the main function for the collaborative filtering approach on user basis. The following steps are
    performed in this function:

    1. first data is reduced to get better results and faster recommendations
    2. utility matrix is created
    3. calculate similarities between frontend user and other users
    4. create group of most similar user to the frontend user
    5. calculate the average game rating in this user group
    6. user the highest average game ratings in this group as a prediction for frontend user
    '''
    # get all data to compare
    data = get_recommendation_data(data, min_number_ratings_game=50)

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
    sorted_pred, pred_info = predict(data, threshold_min_number_ratings_per_game=5)

    sorted_pred = sorted_pred.to_frame().reset_index()
    return sorted_pred[:num_recommendations].to_dict(orient="records")
