
# Questions Monday:
# - what approaches should we try?
# - how many approaches should we try?
# - is this true: first step - measure similarity of user, second step - calculate prediction based on similar users

# Questions Group:
# - Cosine similarity (has to be calculated between new user and existing users)
# - what would schnittstelle look like? get data directly from front end or from data base (database better!)?

import pandas as pd
import numpy as np


def get_recommendation_data():

    # df = pd.read_json('')
    data = pd.read_csv('../Data/test_data/test.csv', sep=',', header=0)
    print(data.shape)
    return data


def prepare_data(data):
    # create utility matrix
    data = data.pivot(index='user', columns='name', values='rating').fillna(0)  # zero means worst possible rating

    #print(data)
    return data


def get_cosine_similarity(x, y):
    numerator = np.dot(x, y)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)

    # sanity check: a and b must be non-zero vectors
    if denominator > 0:
        sim = numerator / denominator
    else:
        sim = 0

    return sim


def calculate_cosine_similarity(data, new_user):

    # get data of requested items
    item_requested = data.loc[new_user].to_numpy()
    position_requested_item = list(data.index).index('4Corners')
    print("-----item_requested: ", item_requested, "index number: ", position_requested_item)

    # empty list to collect results
    similarities = []

    # compute similarity for all user
    for i in range(len(data.index)):
        # for test purposes
        #if i == 15:
        #   break
        #print("run", i)

        if i != position_requested_item:
            # get item_to_compare
            item_to_compare = data.iloc[i].to_numpy()
            print("------item_to_compare: ", item_to_compare)

            # compare both items (item_requested and item_to_compare)
            sim = get_cosine_similarity(x=item_requested, y=item_to_compare)
            similarities.append((i, sim))

    # sort pairs
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    print(sorted_similarities)

    return [sorted_similarities, item_requested]


def calculate_baseline(method, data):
    if method == 'average':
        # calculate average rating for each game
        numerator = data.apply(np.sum, axis=0)
        denominator = data.apply(np.count_nonzero, axis=0)

        # calculate baseline and set denominator 0 if less than x reviews
        denominator = [elem if elem >= 20 else 0 for elem in denominator]
        baseline = numerator / denominator
        # replace nan and inf with 0 rating
        baseline = baseline.replace([np.inf, -np.inf], np.nan).fillna(value=0)

        return baseline

def predict(data, similarities, item_requested):
    # get group of most similar user
    similar_users = list(filter(lambda x: x[1] >= 0.7, similarities))  # TODO: maybe change 0.7% ? User could only have less percentages
    similar_users = [i[0] for i in similar_users]
    data_prediction = data.iloc[similar_users]

    # create data frame with games user has not rated yet
    item_requested_boolean = [not bool(x) for x in item_requested]
    # select only games user has not rated
    data_prediction = data_prediction.loc[:, item_requested_boolean]

    # calculate baseline
    baseline = calculate_baseline(data=data_prediction, method='average')

    # calculate prediction
    numerator = data_prediction.apply(np.sum, axis=0)  # sum ratings per game
    denominator = data_prediction.apply(np.count_nonzero, axis=0)  # count number of ratings
    denominator_prepared = [elem if elem >= 2 else 0 for elem in denominator]  # only use pred if more than 2 reviews else rating of 0

    pred_similar_users = numerator / denominator_prepared
    pred_similar_users = pred_similar_users.replace([np.inf, -np.inf], np.nan).fillna(value=0)

    # use baseline for all games without proper review
    pred = pred_similar_users.combine(baseline, lambda x, y: y if x == 0 else x)

    # add information to table
    pred_info = pd.concat([pred, denominator, numerator], axis=1)
    pred_info = pred_info.sort_values(by=[0], ascending=False)

    # sort predictions
    sorted_pred = pred.sort_values(ascending=False)

    return [sorted_pred, pred_info]


if __name__ == "__main__":
    # get data from database to work with
    data = get_recommendation_data()

    # prepare data
    data = prepare_data(data=data)

    # get new user name
    new_user = "4Corners"  # from database / frontend?

    # calculate similarities
    results = calculate_cosine_similarity(data=data, new_user=new_user)
    sorted_similarities = results[0]
    item_requested = results[1]

    # predict (can also use other models)
    prediction = predict(data=data,
                         similarities=sorted_similarities,
                         item_requested=item_requested)

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
