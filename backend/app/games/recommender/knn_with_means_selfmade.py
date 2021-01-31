import json
import time
import pandas as pd
from .myKNNwithMeansAlgorithm import MyKnnWithMeans


def selfmade_KnnWithMeans_approach(target_ratings: pd.DataFrame):
    start_time = time.time()
    # convert target_ratings dataframe to list of tuples:
    target_ratings = list(target_ratings_df.to_records(index=False))

    # variables:
    k = 40
    min_k = 5

    # get similarity matrix:
    sim_matrix = get_similarity_matrix_from_file(target_ratings_df['game_key'].tolist())

    with open('../Data/Recommender/item-means-reduced_dataset.json') as fp:
        # convert keys to int:
        item_means = {int(key): value for key, value in json.load(fp).items()}

    myKNN = MyKnnWithMeans(sim_matrix, target_ratings, item_means, k, min_k)

    predictions = myKNN.predict_all_games()
    sorted_predictions = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))

    sorted_predictions_list = [{'game_key': k, 'estimate': v} for k, v in sorted_predictions.items()]

    print("--- %s seconds ---" % (time.time() - start_time))
    return sorted_predictions_list[:50]



def get_similarity_matrix_from_db(games_rated_by_target_user):
    # TODO: import of sim_matrix from DB

    # long sim_matrix to wide format:
    sim_matrix_wide = sim_matrix_long.pivot(index='game_key', columns='game_key_2', values='value')

    # convert column names of sim_matrix to int:
    sim_matrix_wide.columns = sim_matrix_wide.columns.astype(int)

    # extract only information for given items:
    sim_matrix_wide = sim_matrix_wide[games_rated_by_target_user]

    return sim_matrix_wide