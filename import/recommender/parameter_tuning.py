from surprise import Reader, Dataset, SVD, NMF, KNNWithMeans, KNNBasic, KNNWithZScore, CoClustering, SlopeOne, dump
from surprise.model_selection import cross_validate
from recommender.lukas_recommender_playground import import_all_reviews


def parameter_tuning():
    """
    After deciding to use the KNNWithMeans algorithm our next step is to tune its parameters to further increase its
    accuracy. There are three parameters we can tune:
    (1) The similarity options, in particular which option we use for computing the similarity matrix. [*]
    (2) The min_k parameter.
    (3) The k parameter.


    1. Sim options:
        We can decide between using the naive cosine similarity, pearson similarity (centred cosine similarity)
        or MSD (mean squared differences). Since the pearson similarity outperforms the others we stick to it.
    2. The min_k parameter:
        The minimum number of neighbors to take into account for computing the weighted adjusted ratings. If less
        than min_k neighbors are available, meaning that not enough games have been rated by the user, that have a
        similarity of >= 0 the prediction is equal to the average rating for the particular game.
    3. The k parameter:
        The maximum number of neighbors to take into account for computing the weighted adjusted ratings. In our case
        the k games rated by the target user that are most similar to the game we are trying to predict.
        We focus on this parameter below.


    More information can be found here:
    https://surprise.readthedocs.io/en/stable/knn_inspired.html#surprise.prediction_algorithms.knns.KNNWithMeans


    As a result we chose the following parameters in our production environment:
    (1) Pearson correlation (centred cosine similarity)
    (2) k = 40
    (3) min_k = 5


    [*] Actually the similarity options include another parameter that determines whether we use item-item or user-user similarities.
     Since we already distinguished between the two in our benchmarking we focus purely on which approach to use for
     computing the similarity matrix here.
    """

    # import reduced dataset:
    df = import_all_reviews('C:/Users/lukas/PycharmProjects/board-game-recommender/import/Data/Joined/Results/Reviews_Reduced_SMALL.csv')

    # check for duplicates:
    duplicates = len(df) - len(df.drop_duplicates(subset=['game_key', 'user_key']))

    # drop duplicates:
    df = df.drop_duplicates(subset=['game_key', 'user_key'])
    print('duplicates removed: ' + str(duplicates))

    ## Surprise:
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(df[['user_key', 'game_key', 'rating']], reader)

    results = []

    sim_option = {'name': 'cosine', 'user_based': False}
    min_k = 5

    # try out different parameters for k:
    k_parameter = list(range(10, 80, 10))
    min_k_parameter = [1, 5, 10]

    # Cross validate:
    for k in k_parameter:
        for min_k in min_k_parameter:
            algo = KNNWithMeans(k=k, min_k=min_k, sim_options=sim_option)
            results.append(
                cross_validate(algo, data, measures=['RMSE'], cv=3, return_train_measures=True, n_jobs=-3, verbose=True))


    for i, result in enumerate(results):
        print('k = ' + str(k_parameter[i]) + '\t \t RMSE Score: \t' + str(result['test_rmse'].mean()) + '\t\t Fit-Time: ' + str(
            result['fit_time']) + '\t\t Train-Time: ' + str(result['test_time']))



if __name__ == '__main__':
    parameter_tuning()
