# This script was used to test if the surprise package would be a good fit for our recommender.


from baseline_preparation import *
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from surprise import Reader, Dataset, SVD, NMF, accuracy, KNNWithMeans, KNNBasic, KNNWithZScore, CoClustering, SlopeOne, dump
from surprise.model_selection import train_test_split, cross_validate
from surprise.trainset import Trainset
from numpy import count_nonzero
from collections import defaultdict
from sklearn.metrics.pairwise import pairwise_distances, cosine_similarity
import csv
import time


def train_surprise_model(data, sim_option, k, min_k):
    # get data in a format surprise can work with
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(data[['user_key', 'game_key', 'rating']], reader)

    # build trainset from the whole datset
    trainset = data.build_full_trainset()
    #trainset, testset = train_test_split(data, test_size=0.2)
    print('Number of users: ', trainset.n_users)
    print('Number of items: ', trainset.n_items)

    # create model
    sim_option = {'name': 'cosine', 'user_based': False}
    k = 10
    min_k = 5
    algo = KNNWithMeans(k=k, min_k=min_k, sim_options=sim_option)

    # fit model
    algo.fit(trainset)

    return algo


def predict_with_model(trained_model, user_key):
    # predict for all games
    all_game_keys = trained_model.trainset._raw2inner_id_items
    all_game_keys = list(all_game_keys.keys())

    predictions = []
    trained_model.predict(uid=58415, iid=100002, verbose=True)
    for elem in all_game_keys:
        predictions.append(trained_model.predict(user_key, elem))

    return predictions


def main():
    start_time = time.time()
    df = get_recommendation_data(link='../Data/Joined/Results/Reviews.csv',
                                 min_number_ratings_game=250,
                                 min_number_ratings_user=10,
                                 size_user_sample=50_000,
                                 seed=56)  # None for random, int for comparison

    # add new user to data

    algo = train_surprise_model(data=df,
                                sim_option={'name': 'cosine', 'user_based': False},
                                k=10,
                                min_k=5)

    pred = predict_with_model(trained_model=algo,
                              user_key=167735)

    end_time = time.time()
    print(end_time-start_time)


main()

# 4000 games (more than 500 ratings per game)
# number user
# 10_000 - 30 sec
# 50_000 - 70 sec
# 100_000 - 2 min

# 10_500 games (more than 100 ratings per game)
# number user
# 10_000 -  50 sec
# 50_000 -  2 min
# 100_000 - ?
