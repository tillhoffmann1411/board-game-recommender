
# Questions Monday:
# - what approaches should we try?
# - how many approaches should we try?
# - is this true: first step - measure similarity of user, second step - calculate prediction based on similar users

# Questions Group:


import pandas as pd
import numpy as np


def get_recommendation_data():

    # df = pd.read_json('')
    data = pd.read_csv('../Data/test_data/test_5000.csv', sep=',', header=0)
    print(data.shape)

    # filter in sql query - only get data from users when they are also rated at least one same game with new_user
    return data


def prepare_data(data):
    # create utility matrix
    data_pivot = data.pivot(index='user', columns='name', values='rating').fillna(0)  # zero means worst possible rating

    # calculate sparsity of matrix
    print(len(data) / (len(data)*len(data.columns)))
    # sparsity of 0.005 -> collaborative filtering might not be best option

    return data_pivot


def get_cosine_similarity(x, y):
    numerator = np.dot(x, y)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)

    # a and b must be non-zero vectors
    if denominator > 0:
        sim = numerator / denominator
    else:
        sim = 0

    return sim


def calculate_cosine_similarity(data, new_user):
    # get items of requested user
    item_requested = data.loc[new_user].to_numpy()
    position_requested_item = list(data.index).index('4Corners')
    print("-----item_requested: ", item_requested, "index number: ", position_requested_item)

    # create empty list to collect results
    similarities = []

    # compute similarity for all user
    for i in range(len(data.index)):
        if i != position_requested_item:
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


if __name__ == "__main__":
    # get data from database
    data = get_recommendation_data()
    # get new user name for recommendation
    new_user = "4Corners"  # from frontend?

    # prepare data
    data = prepare_data(data=data)

    # calculate similarities
    result_cosine_similarity = calculate_cosine_similarity(data=data, new_user=new_user)

    # calculate baseline rating
    baseline = calculate_baseline(data=data,
                                  item_requested=result_cosine_similarity[1],
                                  method="average",
                                  threshold_min_number_ratings_per_game=20)

    # prepare data for prediction
    prediction_data = prepare_prediction_data(data=data,
                                              item_requested=result_cosine_similarity[1],
                                              similarities=result_cosine_similarity[0],
                                              threshold_filter_similar_user=0.7)

    # predict (can also use other models) - average rating in user group
    prediction = predict(data=prediction_data,
                         baseline=baseline,
                         threshold_min_number_ratings_per_game=2)

    print(prediction[1])
    prediction[1].to_csv(path_or_buf='/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data/pred_res_info.csv')


    ### evaluate different recommender approaches
    ## cosine similarity
    # - i have to calculate ratings in frontend - can take much time
    # -
    ## centered cosine similarity
    ## matrix factorization
    ## tree model - xg boost
    ## k-d trees?
    ## knn
    ## svm
    ## regression

    # chose best approach
