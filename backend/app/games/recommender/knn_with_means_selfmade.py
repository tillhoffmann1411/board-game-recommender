import json
import time
import pandas as pd
from .myKNNwithMeansAlgorithm import MyKnnWithMeans


def selfmade_KnnWithMeans_approach(target_user_key: int, target_ratings: pd.DataFrame):
    start_time = time.time()
    # convert target_ratings dataframe to list of tuples:
    target_ratings = list(target_ratings.to_records(index=False))

    # variables:
    k = 40
    min_k = 1
    sim_matrix = pd.read_csv('app/games/recommender/Data/item-item-sim-matrix-surprise-full_dataset.csv', index_col=0)

    # convert column names of sim_matrix to int:
    sim_matrix.columns = sim_matrix.columns.astype(int)

    with open('app/games/recommender/Data/item-means-full_dataset.json') as fp:
        # convert keys to int:
        item_means = {int(key): value for key, value in json.load(fp).items()}

    myKNN = MyKnnWithMeans(sim_matrix, target_ratings, item_means, k, min_k)

    predictions = myKNN.predict_all_games(user_key=target_user_key)
    sorted_predictions = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))

    sorted_predictions_list = [{'game_key': k, 'estimate': v} for k, v in sorted_predictions.items()]

    print("--- %s seconds ---" % (time.time() - start_time))
    return sorted_predictions_list
