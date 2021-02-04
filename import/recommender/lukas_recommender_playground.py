import pandas as pd
import numpy as np
from surprise import Reader, Dataset, SVD, NMF, accuracy, KNNWithMeans, KNNBasic, KNNWithZScore, CoClustering, SlopeOne, \
    dump
from surprise.model_selection import train_test_split, cross_validate

from sklearn.metrics.pairwise import pairwise_distances, cosine_similarity
import time
import json

from recommender.myKNNwithMeansAlgorithm import MyKnnWithMeans

"""
https://medium.com/hacktive-devs/recommender-system-made-easy-with-scikit-surprise-569cbb689824

Reduced Dataset:
Unique users: 44894
Unique games: 312

How to overcome sparcity problem:
https://medium.com/ai-in-plain-english/how-to-improve-recommendations-for-highly-sparse-datasets-using-hybrid-recommender-systems-1a4366e65cff

Overcome sparcity: Use content based predictor first and then apply collaborative filtering.

"""


def get_similarity_matrix(games_rated_by_target_user,
                          path='../Data/Recommender/item-item-sim-matrix-surprise-Reduced_dataset-LONG_FORMAT.csv'):
    # import sim_matrix in long format from csv:
    sim_matrix_long = pd.read_csv(path)

    # remove first column (unnamed):
    sim_matrix_long.drop(sim_matrix_long.columns[0], axis=1, inplace=True)

    # rename first column:
    sim_matrix_long.rename(columns={'index': 'game_key'}, inplace=True)

    start_time = time.time()
    # long sim_matrix to wide format:
    sim_matrix_wide = sim_matrix_long.pivot(index='game_key', columns='game_key_2', values='value')
    print("--- %s seconds ---" % (time.time() - start_time))

    # convert column names of sim_matrix to int:
    sim_matrix_wide.columns = sim_matrix_wide.columns.astype(int)


    ### this part will later be replaced by the SQL query, that takes care of this:
    # extract only information for given items:
    sim_matrix_wide = sim_matrix_wide[games_rated_by_target_user]

    return sim_matrix_wide


def import_all_reviews():
    import_path = 'C:/Users/lukas/PycharmProjects/board-game-recommender/import/Data/Joined/Results/Reviews_Reduced.csv'
    df = pd.read_csv(import_path)
    # keep only important columns:
    df = df[['game_key', 'user_key', 'rating']]
    return df


def reduce_reviews(df):
    # keep only games with > 5000 reviews:
    num_reviews = df.game_key.value_counts()
    df = df[df.game_key.isin(num_reviews.index[num_reviews.gt(5000)])]

    num_reviews2 = df.game_key.value_counts()

    # take only sample of users: 10000
    users_sample = pd.Series(df['user_key'].unique())
    users_sample = users_sample.sample(n=10000, replace=False)
    users_sample = users_sample.tolist()
    df = df[df.user_key.isin(users_sample)]

    # take only sample of games: 50%
    game_sample = pd.Series(df['game_key'].unique())
    game_sample = game_sample.sample(frac=0.5, replace=False)
    game_sample = game_sample.tolist()
    df = df[df.game_key.isin(game_sample)]

    num_users = df['user_key'].nunique()
    num_games = df['game_key'].nunique()

    print('Unique users: ' + str(num_users))
    print('Unique games: ' + str(num_games))

    # remove duplicates:
    duplicates = len(df) - len(df.drop_duplicates(subset=['game_key', 'user_key']))
    print('duplicates removed: ' + str(duplicates))
    df.drop_duplicates(subset=['game_key', 'user_key'], inplace=True)

    return df


def reduce_reviews2(df):
    # keep only games with > 6000 reviews:
    num_reviews = df.game_key.value_counts()
    df = df[df.game_key.isin(num_reviews.index[num_reviews.gt(6000)])]

    num_users = df['user_key'].nunique()
    num_games = df['game_key'].nunique()

    # take only sample of users: 100000
    users_sample = pd.Series(df['user_key'].unique())
    users_sample = users_sample.sample(n=100000, replace=False)
    users_sample = users_sample.tolist()
    df = df[df.user_key.isin(users_sample)]

    print('Unique users: ' + str(num_users))
    print('Unique games: ' + str(num_games))

    # remove duplicates:
    duplicates = len(df) - len(df.drop_duplicates(subset=['game_key', 'user_key']))
    print('duplicates removed: ' + str(duplicates))
    df.drop_duplicates(subset=['game_key', 'user_key'], inplace=True)

    export_path = 'C:/Users/lukas/OneDrive/Desktop/Reviews_Reduced2.csv'
    df.to_csv(export_path)

    return df


def export_reviews(df):
    export_path = 'C:/Users/lukas/OneDrive/Desktop/Reviews_Reduced.csv'
    df.to_csv(export_path)


def import_reduced_reviews(import_path='../Data/Joined/Results/Reviews_Reduced.csv'):
    df = pd.read_csv(import_path)
    # drop index col:
    df.drop(df.columns[0], axis=1, inplace=True)
    return df


def svd_factorization():
    """
    Predict games for user with user_key = 158123
    """
    target_user_key = 158123

    run_reduce_dataset = True

    # reduce dataset:
    if run_reduce_dataset:
        df = import_all_reviews()
        df_reduced = reduce_reviews(df)
        export_reviews(df_reduced)

    # import reduced dataset:
    df = import_reduced_reviews()

    # check for duplicates:
    duplicates = len(df) - len(df.drop_duplicates(subset=['game_key', 'user_key']))

    # drop duplicates:
    df = df.drop_duplicates(subset=['game_key', 'user_key'])
    print('duplicates removed: ' + str(duplicates))

    # check out our user:
    df_target_user = df[df['user_key'] == target_user_key]

    # build utility matrix:
    data_pivot = df.pivot(index='user_key', columns='game_key', values='rating')

    # calculate sparsity
    sparsity = data_pivot.isnull().sum().sum() / data_pivot.size
    print('Sparcity of utility matrix: ' + str(sparsity))

    # reader belongs to Scikit-surprise
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(df[['user_key', 'game_key', 'rating']], reader)

    # split in training and test set
    trainset, testset = train_test_split(data, test_size=0.2)

    # apply SVD algorithm:
    algo = SVD()
    algo.fit(trainset)
    predictions = algo.test(testset)

    # Evaluation:
    rsme = accuracy.rmse(predictions)
    print('RSME of: ' + str(rsme))

    ### Prediction for target user:
    # Predict ratings for all pairs (u, i) that are NOT in the training set.
    testset = Dataset.load_from_df(df_target_user[['user_key', 'game_key', 'rating']], reader)
    predictions = algo.test(testset)


def collaborative_filtering_selfmade():
    # import reduced dataset:
    df = import_reduced_reviews()

    # build utility matrix:
    utility_matrix = df.pivot(index='user_key', columns='game_key', values='rating')
    utility_matrix_normalized = utility_matrix

    # calculate sparsity
    sparsity = utility_matrix.isnull().sum().sum() / utility_matrix.size
    print('Sparcity of utility matrix: ' + str(sparsity))

    # adjust by global mean:
    global_mean = df['rating'].mean()
    utility_matrix_normalized = utility_matrix_normalized - global_mean

    # adjust by user mean:
    user_mean = utility_matrix_normalized.mean(axis=0)
    utility_matrix_normalized = utility_matrix_normalized - user_mean

    # adjust by item mean:
    item_mean = utility_matrix_normalized.mean(axis=1)
    utility_matrix_normalized = utility_matrix_normalized - user_mean

    ### calculate cosine similarities
    # fill nans with 0
    utility_matrix_normalized = utility_matrix_normalized.fillna(0)
    # calculate cosine similarities for users
    cosine_sim = cosine_similarity(utility_matrix_normalized)

    cosine_sim = pd.DataFrame(cosine_sim)
    # get indexes back:
    cosine_sim.index = utility_matrix_normalized.index
    cosine_sim.columns = utility_matrix_normalized.index

    ### target user
    target_user_key = 93681
    target_user_info = df[df['user_key'] == target_user_key]

    # get n nearest neighbors for target_user:
    target_column = cosine_sim[target_user_key]
    neighbors = pd.DataFrame(target_column.nlargest(n=20))

    # predict ratings using these neighbors by applying weighted average:
    neighbors.reset_index(inplace=True)
    neighbors.rename(columns={neighbors.columns[1]: "cosine_sim"}, inplace=True)
    neighbors_list = neighbors['user_key'].tolist()

    target_matrix = utility_matrix[utility_matrix.index.isin(neighbors_list)]

    temp = neighbors.sort_values('user_key')
    weights = temp['cosine_sim']

    # multiply matrix by weights:
    result = pd.DataFrame(target_matrix.apply(
        lambda x: np.ma.average(np.ma.MaskedArray(x, mask=np.isnan(x)), weights=weights)))

    result.reset_index(inplace=True)
    result.rename(columns={result.columns[1]: "expected_rating"}, inplace=True)

    result = result[result['expected_rating'] != 'masked']
    result.sort_values(by='expected_rating', inplace=True, ascending=False)

    # exclude games he already voted:
    result = result[~result['game_key'].isin(target_user_info.game_key.tolist())]

    print('end')


def collaborative_filtering_using_surprise():
    """
    https://towardsdatascience.com/how-to-build-a-memory-based-recommendation-system-using-python-surprise-55f3257b2cf4
    Predict games for user with user_key = 93681
    """
    target_user_key = 93681

    # import reduced dataset:
    df = import_reduced_reviews()

    # check for duplicates:
    duplicates = len(df) - len(df.drop_duplicates(subset=['game_key', 'user_key']))

    # drop duplicates:
    df = df.drop_duplicates(subset=['game_key', 'user_key'])
    print('duplicates removed: ' + str(duplicates))

    # check out our user:
    df_target_user = df[df['user_key'] == target_user_key]

    # build utility matrix:
    # data_pivot = df.pivot(index='user_key', columns='game_key', values='rating')

    # calculate sparsity
    # sparsity = data_pivot.isnull().sum().sum() / data_pivot.size
    # print('Sparcity of utility matrix: ' + str(sparsity))

    ### Modelling part with Surprise:
    # get data in a format surprise can work with:
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(df[['user_key', 'game_key', 'rating']], reader)

    # Split in trainset and testset
    trainset, testset = train_test_split(data, test_size=0.2)

    print('Number of users: ', trainset.n_users, '\n')
    print('Number of items: ', trainset.n_items, '\n')

    # When surprise creates a Trainset or Testset object, it takes the raw_id’s (the ones that you used in the file
    # you imported), and converts them to so-called inner_id’s (basically a series of integers, starting from 0). You
    # might need to trace back to the original names. Using the items as an example (you can do the same approach
    # with users, just swap iid's with uid's in the code), to get the list of inner_iids, you can use the all_items
    # method. To convert from raw to inner id you can use the to_inner_iid method, and the to_raw_iid to convert back.

    # An example on how to save a list of inner and raw item id’s:
    trainset_iids = list(trainset.all_items())
    iid_converter = lambda x: trainset.to_raw_iid(x)
    trainset_raw_iids = list(map(iid_converter, trainset_iids))

    ## Model parameters: of kNN:
    # Two hyperparameters we can tune:
    # 1. k parameter
    # 2. similarity option
    #   a) user-user vs item-item
    #   b) similarity function (cosine, pearson, msd)

    sim_option = {
        'name': 'pearson', 'user_based': False
    }

    # 3 different KNN Models: KNNBasic, KNNWithMeans, KNNWithZScore
    k = 40
    min_k = 5

    algo = KNNWithMeans(
        k=k, min_k=min_k, sim_options=sim_option
    )

    algo.fit(trainset)

    ## Testing:
    predictions = algo.test(testset)

    accuracy.rmse(predictions)

    # Own similarity matrix:
    sim_matrix_imported = pd.read_csv('../Data/Recommender/selfmade_item-item-similarity-matrix.csv', index_col=0)
    sim_matrix_imported.columns = sim_matrix_imported.columns.astype(int)
    sim_matrix_imported = sim_matrix_imported.to_numpy()

    algo.sim = sim_matrix_imported

    predictions = algo.test(testset)

    accuracy.rmse(predictions)

    # Cross validation:
    skip = True
    if not skip:
        results = cross_validate(
            algo=algo, data=data, measures=['RMSE'],
            cv=5, return_train_measures=True
        )
        results_mean = results['test_rmse'].mean()

    ## Predictions
    # Lets assume we are happy with the method and now want to apply it to the entire data set.

    # Estimate for a specific user a specific item:
    single_item_single_user_prediction = algo.predict(uid=target_user_key, iid=100010, verbose=True)

    # Estimate all items for a specific user:
    list_of_all_items = trainset_raw_iids
    target_predictions = []

    for item in list_of_all_items:
        single_prediction = algo.predict(uid=target_user_key, iid=item)
        target_predictions.append((single_prediction.uid, single_prediction.iid, single_prediction.est))

    # Then sort the predictions for each user and retrieve the k highest ones:
    target_predictions.sort(key=lambda x: x[2], reverse=True)
    n = 20
    top_n = target_predictions[:n]
    top_n = [row[1] for row in top_n]

    print('end')


def benchmark_different_algorithms():
    # import reduced dataset:
    df = import_reduced_reviews()

    # check for duplicates:
    duplicates = len(df) - len(df.drop_duplicates(subset=['game_key', 'user_key']))

    # drop duplicates:
    df = df.drop_duplicates(subset=['game_key', 'user_key'])
    print('duplicates removed: ' + str(duplicates))

    ## Surprise:
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(df[['user_key', 'game_key', 'rating']], reader)

    results = []
    algorithms = [
        'SVD\t\t\t\t\t\t', 'SlopeOne\t\t\t\t', 'CoClustering\t\t\t', 'NMF\t\t\t\t\t\t',
        'KNN_Basic Item-Item\t\t', 'KNN_WithMeans Item-Item\t', 'KNN_WithZScore Item-Item',
        'KNN_Basic User-User\t\t', 'KNN_WithMeans User-User\t', 'KNN_WithZScore User-User'
    ]

    # 1) SVD
    algo = SVD()
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    # 2) Slope One
    algo = SlopeOne()
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    # 3) CoClustering
    algo = CoClustering()
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    # 4) NMF
    algo = NMF()
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    ## K-Nearest Neighbors - Item-Item
    sim_option = {'name': 'cosine', 'user_based': False}
    k = 40
    min_k = 5

    # 5) KNNBasic
    algo = KNNBasic(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    # 6) KNNWithMeans
    algo = KNNWithMeans(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    # 7) KNNWithZScore
    algo = KNNWithZScore(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    ## K-Nearest Neighbors - User - User
    sim_option = {'name': 'cosine', 'user_based': True}
    k = 100
    min_k = 2

    # 8) KNNBasic
    algo = KNNBasic(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    # 9) KNNWithMeans
    algo = KNNWithMeans(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    # 10) KNNWithZScore
    algo = KNNWithZScore(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))

    for algorithm, result in zip(algorithms, results):
        print(algorithm + '\t \t RMSE Score: \t' + str(result['test_rmse'].mean()) + '\t\t Fit-Time: ' + str(
            result['fit_time']) + '\t\t Train-Time: ' + str(result['test_time']))

    print('test')


def create_selfmade_item_item_cosine_similarity_matrix():
    # import reduced dataset:
    df = import_reduced_reviews()

    # build utility matrix:
    utility_matrix = df.pivot(index='game_key', columns='user_key', values='rating')

    # calculate sparsity
    sparsity = utility_matrix.isnull().sum().sum() / utility_matrix.size
    print('Sparcity of utility matrix: ' + str(sparsity))

    # adjust by global mean:
    global_mean = df['rating'].mean()
    utility_matrix_normalized = utility_matrix - global_mean

    # adjust by user mean:
    user_mean = utility_matrix_normalized.mean(axis=0)
    utility_matrix_normalized = utility_matrix_normalized - user_mean

    # adjust by item mean:
    item_mean = utility_matrix_normalized.mean(axis=1)
    utility_matrix_normalized = utility_matrix_normalized - user_mean

    ### calculate cosine similarities
    # fill nans with 0
    utility_matrix_normalized = utility_matrix_normalized.fillna(0)

    # calculate cosine similarities for items
    cosine_sim = cosine_similarity(utility_matrix_normalized)

    cosine_sim = pd.DataFrame(cosine_sim)
    # get indexes back:
    cosine_sim.index = utility_matrix_normalized.index
    cosine_sim.columns = utility_matrix_normalized.index

    # save similarity matrix:
    cosine_sim.to_csv('../Data/Recommender/selfmade_item-item-similarity-matrix.csv')


def train_surprise_model():
    # import reduced dataset:
    df = import_reduced_reviews('C:/Users/lukas/OneDrive/Desktop/Reviews_Reduced.csv')
    df = df[['user_key', 'game_key', 'rating']]

    # drop duplicates:
    df = df.drop_duplicates(subset=['game_key', 'user_key'])

    ### Modelling part with Surprise:
    # get data in a format surprise can work with:
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(df[['user_key', 'game_key', 'rating']], reader)

    # Build trainset from the whole dataset:
    trainsetfull = data.build_full_trainset()
    print('Number of users: ', trainsetfull.n_users, '\n')
    print('Number of items: ', trainsetfull.n_items, '\n')

    # Parameters:
    sim_option = {'name': 'cosine', 'user_based': False}
    k = 10
    min_k = 5

    algo = KNNWithMeans(k=k, min_k=min_k, sim_options=sim_option)

    # Run fit:
    start_time = time.time()
    algo.fit(trainsetfull)
    print("--- %s seconds ---" % (time.time() - start_time))

    ### Test: is it possible to exchange the sim matrix?
    sim_matrix_imported = pd.read_csv('../Data/Recommender/selfmade_item-item-similarity-matrix.csv', index_col=0)
    sim_matrix_imported.columns = sim_matrix_imported.columns.astype(int)
    sim_matrix_imported = sim_matrix_imported.to_numpy()

    a = algo.predict(93681, 100007)
    algo.sim = sim_matrix_imported
    b = algo.predict(93681, 100007)

    # We now need to save the similarity matrix somewhere:
    sim_matrix = algo.sim
    pd.DataFrame(sim_matrix).to_csv('../Data/Recommender/sim_matrix-myKNNWithMeans_item_based_model')

    # Save the precomputed model:
    dump.dump('../Data/Recommender/myKNNWithMeans_item_based_model', algo)


def get_recommendation_for_user_surprise(user_id=123, user_input={100001: 8, 100002: 9, 100003: 5}):
    # load precomputed algo:
    algo = dump.load('../Data/Recommender/myKNNWithMeans_item_based_model')

    # load precomputed sim_matrix:
    sim_matrix_df = pd.read_csv('../Data/Recommende r/myKNNWithMeans_item_based_model')
    sim_matrix = sim_matrix_df.to_numpy()

    ###

    print('end')


def selfmade_approach():
    # import reduced dataset:
    df = import_reduced_reviews('C:/Users/lukas/OneDrive/Desktop/Reviews_Reduced.csv')
    df = df[['user_key', 'game_key', 'rating']]

    # drop duplicates:
    df = df.drop_duplicates(subset=['game_key', 'user_key'])

    ### Modelling part with Surprise:
    # get data in a format surprise can work with:
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(df[['user_key', 'game_key', 'rating']], reader)

    # Build trainset from the whole dataset:
    trainsetfull = data.build_full_trainset()
    print('Number of users: ', trainsetfull.n_users, '\n')
    print('Number of items: ', trainsetfull.n_items, '\n')

    # Parameters:
    sim_option = {'name': 'cosine', 'user_based': False}
    k = 10
    min_k = 5

    algo = KNNWithMeans(k=k, min_k=min_k, sim_options=sim_option)

    # Run fit:
    start_time = time.time()
    algo.fit(trainsetfull)
    print("--- %s seconds ---" % (time.time() - start_time))

    # 1st approach: Calculate for a single user contained in dataset:
    target_user_key = 286189
    target_user_info = df[df['user_key'] == target_user_key]

    # Estimate single game:
    target_game_key = 100098

    # data structures:
    # sim_matrix = ndarray(312,312)
    # xr = defaultdict: 312
    # yr = defaultdict 8787

    # later on replace these by self-written structures
    xr = algo.xr
    yr = algo.yr
    sim_matrix = algo.sim
    item_means = algo.means

    inner_target_uid = algo.trainset.to_inner_uid(target_user_key)
    inner_target_iid = algo.trainset.to_inner_iid(target_game_key)

    # switch: uid and idd:
    x = inner_target_uid
    y = inner_target_iid

    # pred2:
    inner_2_raw_item_ids = algo.trainset._raw2inner_id_items
    # swap keys and values:
    inner_2_raw_item_ids = dict((v, k) for k, v in inner_2_raw_item_ids.items())

    # similarity matrix with raw ids instead of inner surprise ids:
    sim_matrix_df = pd.DataFrame(sim_matrix)
    sim_matrix_df = sim_matrix_df.rename(columns=lambda x: inner_2_raw_item_ids[x])
    sim_matrix_df = sim_matrix_df.rename(index=lambda x: inner_2_raw_item_ids[x])

    target_user_ratings = yr[x]

    # convert from inner to raw:
    target_user_ratings2 = []
    for (inner_iid, rating) in target_user_ratings:
        target_user_ratings2.append((inner_2_raw_item_ids[inner_iid], rating))

    # convert item means from inner to raw:
    item_means2 = {}
    for i, mean in enumerate(item_means):
        item_means2[inner_2_raw_item_ids[i]] = mean

    myKNN = MyKnnWithMeans(sim_matrix=sim_matrix_df, target_user_ratings=target_user_ratings2, item_means=item_means2,
                           k=k, min_k=min_k)
    pred = myKNN.predict_single_game(user_key=target_user_key, game_key=target_game_key)
    pred_surprise = algo.predict(uid=inner_target_uid, iid=inner_target_iid)

    estimate = pred
    print("Estimate for user %s for game %s is %s" % (target_user_key, target_game_key, estimate))

    # Estimate for user not contained in dataset:
    target_user_key = 123456789
    target_game_key = 100098

    user_ratings = [
        (100284, 7),
        (100311, 8),
        (105154, 2),
        (100020, 4),
        (100001, 9),
        (100277, 7),
    ]

    myKNN2 = MyKnnWithMeans(sim_matrix_df, user_ratings, item_means2, k, min_k)
    prediction = myKNN2.predict_single_game(target_user_key, target_game_key)

    # export similarity matrix:
    sim_matrix_df.to_csv('../Data/Recommender/item-item-sim-matrix-surprise.csv')

    # export item means:
    export_path = '../Data/Recommender/item-means.json'
    with open(export_path, 'w') as fp:
        json.dump(item_means2, fp, sort_keys=False, indent=4)

    test = sim_matrix_df.loc[100516, 100284]

    pass


def get_KNN_predictions(target_ratings_df: pd.DataFrame):
    start_time = time.time()
    # convert target_ratings dataframe to list of tuples:
    target_ratings = list(target_ratings_df.to_records(index=False))

    # variables:
    k = 40
    min_k = 5

    # get similarity matrix:
    sim_matrix = get_similarity_matrix(target_ratings_df['game_key'].tolist())

    with open('../Data/Recommender/item-means-reduced_dataset.json') as fp:
        # convert keys to int:
        item_means = {int(key): value for key, value in json.load(fp).items()}

    myKNN = MyKnnWithMeans(sim_matrix, target_ratings, item_means, k, min_k)

    predictions = myKNN.predict_all_games()
    sorted_predictions = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))

    sorted_predictions_list = [{'game_key': k, 'estimate': v} for k, v in sorted_predictions.items()]

    print("--- %s seconds ---" % (time.time() - start_time))
    return sorted_predictions_list


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

    # export sim_matrix:
    sim_matrix.to_csv('../Data/Recommender/item-item-sim-matrix-surprise-Reduced_dataset.csv')

    # convert item means from inner to raw:
    item_means_raw_ids = {}
    for i, mean in enumerate(item_means):
        item_means_raw_ids[inner_2_raw_item_ids[i]] = mean

    # export item means:
    export_path = '../Data/Recommender/item-means-Reduced_dataset.json'
    with open(export_path, 'w') as fp:
        json.dump(item_means_raw_ids, fp, sort_keys=False, indent=4)

    ## create sim matrix in long format:
    # get index as column:
    column_names = list(sim_matrix.columns.values)
    sim_matrix.reset_index(level=0, inplace=True)

    # convert df from wide to long:
    sim_matrix_long = pd.melt(sim_matrix, id_vars='index', value_vars=column_names, var_name='game_key_2')
    sim_matrix_long.rename(columns={'index': 'game_key'})

    # export long sim matrix:
    sim_matrix_long.to_csv('../Data/Recommender/item-item-sim-matrix-surprise-Reduced_dataset-LONG_FORMAT.csv')

    print("--- %s seconds ---" % (time.time() - start_time))
    print('function end reached')


def main():
    run_method = 9

    if run_method == 1:
        svd_factorization()
    elif run_method == 2:
        collaborative_filtering_selfmade()
    elif run_method == 3:
        collaborative_filtering_using_surprise()
    elif run_method == 4:
        benchmark_different_algorithms()
    elif run_method == 5:
        create_selfmade_item_item_cosine_similarity_matrix()
    elif run_method == 6:
        train_surprise_model()
    elif run_method == 7:
        get_recommendation_for_user_surprise()
    elif run_method == 8:
        selfmade_approach()
    elif run_method == 9:
        user_ratings = pd.DataFrame({'game_key': [100001, 100007, 100003, 100006, 100005, 100013, 100011, 100008, 100004, 100002],
                                     'rating': [8, 10, 4, 8, 2, 10, 6, 8, 6, 10]})
        result = get_KNN_predictions(user_ratings)
    elif run_method == 10:
        create_similarity_matrix()


main()
