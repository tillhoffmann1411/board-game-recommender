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

    # get predictions of all games for our target user:
    predictions = myKNN.predict_all_games(user_key=target_user_key)

    # sort predictings descending by prediction:
    sorted_predictions = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))

    # bring predictions into desired output format:
    sorted_predictions_list = [{'game_key': k, 'estimate': v} for k, v in sorted_predictions.items()]

    print("--- %s seconds ---" % (time.time() - start_time))
    return sorted_predictions_list[:50]


def create_similarity_matrix():
    start_time = time.time()

    # import reviews:
    import_path = '../Data/Joined/Results/Reviews_Reduced.csv'
    df = pd.read_csv(import_path)

    # keep only important columns:
    df = df[['game_key', 'user_key', 'rating']]

    # create surprise algorithm object
    sim_option = {'name': 'pearson', 'user_based': False}
    algo = KNNWithMeans(sim_options=sim_option)

    # get data in a format surprise can work with:
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(df[['user_key', 'game_key', 'rating']], reader)

    # Build trainset from the whole dataset:
    trainset_full = data.build_full_trainset()
    print('Number of users: ', trainset_full.n_users, '\n')
    print('Number of items: ', trainset_full.n_items, '\n')

    # fit similarity matrix and calculate item means:
    algo.fit(trainset_full)
    print("--- %s seconds ---" % (time.time() - start_time))

    # save similarity matrix and means from algo object to variable
    sim_matrix = algo.sim
    item_means = algo.means

    # convert numpy array to pd df:
    sim_matrix = pd.DataFrame(sim_matrix)

    # replace inner ids with raw ids:
    raw_2_inner_ids = trainset_full._raw2inner_id_items
    # swap keys and values:
    inner_2_raw_item_ids = dict((v, k) for k, v in raw_2_inner_ids.items())

    # replace inner ids in sim_matrix index and columns by game_keys:
    sim_matrix = sim_matrix.rename(index=inner_2_raw_item_ids)
    sim_matrix = sim_matrix.rename(columns=inner_2_raw_item_ids)

    # convert item means from inner to raw:
    item_means_raw_ids = {}
    for i, mean in enumerate(item_means):
        item_means_raw_ids[inner_2_raw_item_ids[i]] = mean

    # export item means:
    export_path = '../Data/Recommender/item-means-Reduced_dataset.json'
    with open(export_path, 'w') as fp:
        json.dump(item_means_raw_ids, fp, sort_keys=False, indent=4)

    # TODO: export item means to DB instead of CSV!

    ## create sim matrix in long format:
    # get index as column:
    column_names = list(sim_matrix.columns.values)
    sim_matrix.reset_index(level=0, inplace=True)

    # convert df from wide to long:
    sim_matrix_long = pd.melt(sim_matrix, id_vars='index', value_vars=column_names, var_name='game_key_2')
    sim_matrix_long.rename(columns={'index': 'game_key'})

    # export long sim matrix:
    sim_matrix_long.to_csv('../Data/Recommender/item-item-sim-matrix-surprise-Reduced_dataset-LONG_FORMAT.csv')

    # TODO: export sim matrix to DB instead of CSV!

    print("--- %s seconds ---" % (time.time() - start_time))
    print('function end reached')
