import pandas as pd
import numpy as np
from surprise import Reader, Dataset, SVD, NMF, accuracy, KNNWithMeans, KNNBasic, KNNWithZScore, CoClustering, SlopeOne, dump
from surprise.model_selection import train_test_split, cross_validate
from surprise.trainset import Trainset
from sklearn.metrics.pairwise import pairwise_distances, cosine_similarity
import time
import heapq


class MyKnnWithMeans:
    def __init__(self, sim_matrix, target_user_ratings, item_means, k=3, min_k=1):
        self.k = k
        self.min_k = min_k
        self.sim_matrix = sim_matrix
        self.target_user_ratings = target_user_ratings
        self.item_means = item_means

        # check if games in target ratings exist in sim_matrix
        # if not remove them:
        for rating_tuple in list(target_user_ratings):
            if rating_tuple[0] not in self.sim_matrix:
                target_user_ratings.remove(rating_tuple)

    def predict_all_games(self):
        all_games = [k for k, _ in self.item_means.items()]
        games_with_rating = [x[0] for x in self.target_user_ratings]
        games_to_predict = list(set(all_games)-set(games_with_rating))

        predictions = {}
        for game in games_to_predict:
            single_pred = self.predict_single_game(game)
            predictions[game] = single_pred

        return predictions


    def predict_single_game(self, game_key):
        x = game_key

        # get similarities of the games the user has already rated to the target game:
        neighbors = [(x2, self.sim_matrix.loc[x, x2], r) for (x2, r) in self.target_user_ratings]

        # keep k games that are most similar to the target game:
        k_neighbors = heapq.nlargest(self.k, neighbors, key=lambda t: t[1])

        est = self.item_means[x]

        # compute weighted average
        sum_sim = sum_ratings = actual_k = 0
        for (nb, sim, r) in k_neighbors:
            if sim > 0:
                sum_sim += sim
                sum_ratings += sim * (r - self.item_means[nb])
                actual_k += 1

        try:
            est += sum_ratings / sum_sim
        except ZeroDivisionError:
            pass  # return mean

        # make sure that estimate does not exceed the max_rating of 10:
        if est > 10:
            est = 10

        return est










