import json
import time
import pandas as pd
import os
import heapq

from django_pandas.io import read_frame
from django.db import connection
from ..models import ItemSimilarityMatrix


def selfmade_KnnWithMeans_approach(target_ratings_df: pd.DataFrame):
    # convert target_ratings dataframe to list of tuples:
    target_ratings = list(target_ratings_df.to_records(index=False))

    # variables:
    k = 40
    min_k = 5

    # get similarity matrix:
    sim_matrix = get_similarity_matrix_from_db(target_ratings_df['game_key'].tolist())

    path = os.path.dirname(os.path.abspath(__file__)) + '/item-means-reduced_dataset.json'
    with open(path) as fp:
        # convert keys to int:
        item_means = {int(key): value for key, value in json.load(fp).items()}

    myKNN = MyKnnWithMeans(sim_matrix, target_ratings, item_means, k, min_k)

    predictions = myKNN.predict_all_games()
    sorted_predictions = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))

    sorted_predictions_list = [{'game_key': k, 'estimate': v} for k, v in sorted_predictions.items()]

    # print("--- %s seconds ---" % (time.time() - start_time))
    return sorted_predictions_list[:50]


def get_similarity_matrix_from_db(games_rated_by_target_user):
    # Import similarity matrix of games rated by our target user
    # example: let's say he rated 10 games
    # in this case the similarity matrix will contain 10*4000 = 40000 rows:
    sim_matrix_long = read_frame(ItemSimilarityMatrix.objects.filter(game_one__in=games_rated_by_target_user))
    sim_matrix_long = sim_matrix_long.rename(
        columns={'game_one': 'game_key', 'game_two': 'game_key_2', 'similarity': 'value'}
    )

    # long sim_matrix to wide format:
    sim_matrix_wide = sim_matrix_long.pivot(index='game_key', columns='game_key_2', values='value')

    # convert column names of sim_matrix to int:
    sim_matrix_wide.columns = sim_matrix_wide.columns.astype(int)

    return sim_matrix_wide


class MyKnnWithMeans:
    def __init__(self, sim_matrix, target_user_ratings, item_means, k=40, min_k=1):
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

        neighbors = [(x2, self.sim_matrix.loc[x2, x], r) for (x2, r) in self.target_user_ratings]

        # keep k games with highest ratings:
        k_neighbors = heapq.nlargest(self.k, neighbors, key=lambda t: t[1])

        est = self.item_means[x]

        # compute weighted average
        sum_sim = sum_ratings = actual_k = 0
        for (nb, sim, r) in k_neighbors:
            if sim > 0:
                sum_sim += sim
                sum_ratings += sim * (r - self.item_means[nb])
                actual_k += 1

        if actual_k < self.min_k:
            sum_ratings = 0

        try:
            est += sum_ratings / sum_sim
        except ZeroDivisionError:
            pass  # return mean

        # make sure that estimate does not exceed the max_rating of 10:
        if est > 10:
            est = 10

        return est
