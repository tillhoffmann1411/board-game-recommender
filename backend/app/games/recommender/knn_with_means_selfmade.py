import pandas as pd
import numpy as np
import time
from surprise import Reader, Dataset, SVD, NMF, accuracy, KNNWithMeans, KNNBasic, KNNWithZScore, CoClustering, SlopeOne, \
    dump
from surprise.model_selection import train_test_split, cross_validate
from .myKNNwithMeansAlgorithm import MyKnnWithMeans


def selfmade_KnnWithMeans_approach(target_user_key: int, target_ratings: pd.DataFrame):
    start_time = time.time()
    # convert target_ratings dataframe to list of tuples:
    target_ratings = list(target_ratings.to_records(index=False))

    # variables:
    k = 40
    min_k = 5
    sim_matrix = pd.read_csv('../Data/Recommender/item-item-sim-matrix-surprise-full_dataset.csv_dataset.csv', index_col=0)
    
    # sim_matrix_long = pd.read_csv('../Data/Recommender/item-item-sim-matrix-surprise-small_dataset-LONG_FORMAT.csv', index_col=0)
    # long sim_matrix to wide format:
    # sim_matrix_wide = sim_matrix_long.pivot(index='game_key', columns='game_key_2', values='value')

    # convert column names of sim_matrix to int:
    sim_matrix.columns = sim_matrix.columns.astype(int)

    with open('../Data/Recommender/item-means-full_dataset.json') as fp:
        # convert keys to int:
        item_means = {int(key): value for key, value in json.load(fp).items()}

    myKNN = MyKnnWithMeans(sim_matrix, target_ratings, item_means, k, min_k)

    predictions = myKNN.predict_all_games(user_key=target_user_key)
    sorted_predictions = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))

    sorted_predictions_list = [{'game_key':k, 'estimate':v} for k, v in sorted_predictions.items()]

    print("--- %s seconds ---" % (time.time() - start_time))
    return sorted_predictions_list