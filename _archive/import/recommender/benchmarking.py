from surprise import Reader, Dataset, SVD, NMF, KNNWithMeans, KNNBasic, KNNWithZScore, CoClustering, SlopeOne, \
    dump
from surprise.model_selection import cross_validate
from recommender.lukas_recommender_playground import import_all_reviews


def benchmark_different_algorithms():
    """
    Run a cross validation procedure for all algorithms available in the Surprise package, reporting accuracy
    measures (RMSE) and computation times (train and fit).

    For our dataset the result was that the item-item based KNN approach taking into account rating means
    yielded the highest RMSE score.
    """

    # import reduced dataset:
    df = import_all_reviews()

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

    # 1) SVD (Single Value Decomposition)
    algo = SVD()
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    # 2) Slope One
    algo = SlopeOne()
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    # 3) CoClustering
    algo = CoClustering()
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    # 4) NMF
    algo = NMF()
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    ## K-Nearest Neighbors - Item-Item
    sim_option = {'name': 'cosine', 'user_based': False}
    k = 40
    min_k = 5

    # 5) KNNBasic
    algo = KNNBasic(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    # 6) KNNWithMeans
    algo = KNNWithMeans(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    # 7) KNNWithZScore
    algo = KNNWithZScore(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    ## K-Nearest Neighbors - User - User
    sim_option = {'name': 'cosine', 'user_based': True}
    k = 100
    min_k = 2

    # 8) KNNBasic
    algo = KNNBasic(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    # 9) KNNWithMeans
    algo = KNNWithMeans(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    # 10) KNNWithZScore
    algo = KNNWithZScore(k=k, min_k=min_k, sim_options=sim_option)
    results.append(
        cross_validate(algo, data, measures=['RMSE'], cv=5, return_train_measures=True, n_jobs=-3, verbose=True))

    for algorithm, result in zip(algorithms, results):
        print(algorithm + '\t \t RMSE Score: \t' + str(result['test_rmse'].mean()) + '\t\t Fit-Time: ' + str(
            result['fit_time']) + '\t\t Train-Time: ' + str(result['test_time']))


if __name__ == '__main__':
    benchmark_different_algorithms()
