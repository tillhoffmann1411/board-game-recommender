import os
import sys
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz, load_npz, vstack, hstack, lil_matrix
import implicit
import pickle
from implicit.evaluation import train_test_split, precision_at_k, mean_average_precision_at_k
from baseline_main import *


def load_data():
    '''load the MovieLens 1m dataset in a Pandas dataframe'''
    ratings = pd.read_csv('/Users/maxmaiberger/Downloads/ml-1m/ratings.dat', delimiter='::', header=None,
        names=['user_id', 'movie_id', 'rating', 'timestamp'],
        usecols=['user_id', 'movie_id', 'rating'], engine='python')

    return ratings


def sparse_matrices(df):
    '''creates the sparse user-item and item-user matrices'''

    # using a scalar value (40) to convert ratings from a scale (1-5) to a like/click/view (1)
    alpha = 40

    sparse_user_item = csr_matrix(([alpha]*len(df['movie_id']), (df['user_id'], df['movie_id'])))
    # transposing the item-user matrix to create a user-item matrix
    sparse_item_user = sparse_user_item.T.tocsr()
    # save the matrices for recalculating user on the fly
    save_npz("/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/sparse_user_item.npz", sparse_user_item)
    save_npz("/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/sparse_item_user.npz", sparse_item_user)

    return sparse_user_item, sparse_item_user


def map_movies(movie_ids):
    '''takes a list of movie_ids and returns a list of dictionaries with movies information'''
    df = pd.read_csv('/Users/maxmaiberger/Downloads/ml-1m/movies.dat', delimiter='::', header=None,
        names=['movie_id', 'title', 'genre'], engine='python')

    # add years to a new column 'year' and remove them from the movie title
    df['year'] = df['title'].str[-5:-1]
    df['title'] = df['title'].str[:-6]

    # creates an ordered list of dictionaries with the movie information for all movie_ids
    mapped_movies = [df[df['movie_id'] == i].to_dict('records')[0] for i in movie_ids]

    return mapped_movies


def map_users(user_ids):
    '''takes a list of user_ids and returns a list of dictionaries with user information'''
    df = pd.read_csv('/Users/maxmaiberger/Downloads/ml-1m/users.dat', delimiter='::', header=None,
        names=['user_id', 'gender', 'agerange', 'occupation', 'timestamp'], engine='python')
    df = df.drop(['timestamp'], axis=1)

    mapped_users = [df[df['user_id'] == user].to_dict('records')[0] for user in user_ids]

    return mapped_users


def most_similar_items(item_id, n_similar=10):
    '''computes the most similar items'''
    with open('/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/model.sav', 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    similar, _ = zip(*model.similar_items(item_id, n_similar)[1:])

    return map_movies(similar)


def most_similar_users(user_id, n_similar=10):
    '''computes the most similar users'''
    sparse_user_item = load_npz("/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/sparse_user_item.npz")

    with open('/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/model.sav', 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    # similar users gives back [(users, scores)]
    # we want just the users and not the first one, because that is the same as the original user
    similar, _ = zip(*model.similar_users(user_id, n_similar)[1:])

    # original users items
    original_user_items = list(sparse_user_item[user_id].indices)

    # # this maps back user_ids to their information, which is useful for visualisation
    similar_users_info = map_users(similar)
    # # now we want to add the items that a similar user has rated
    for user_info in mapped:
        # we create a list of items that correspond to the similar user ids
        # then compare that in a set operation to the original user items
        # as a last step we add it as a key to the user information dictionary
        user_info['items'] = set(list(sparse_user_item[user_info['user_id']].indices)) & set(original_user_items)

    return similar_users_info


def model():
    '''computes p@k and map@k evaluation metrics and saves model'''
    sparse_item_user = load_npz("/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/sparse_item_user.npz")

    train, test = train_test_split(sparse_item_user, train_percentage=0.8)

    model = implicit.als.AlternatingLeastSquares(factors=100,
                                                 regularization=0.1, iterations=20, calculate_training_loss=False)
    model.fit(train)

    with open('/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/model.sav', 'wb') as pickle_out:
        pickle.dump(model, pickle_out)

    p_at_k = precision_at_k(model, train_user_items=train, test_user_items=test, K=10)
    m_at_k = mean_average_precision_at_k(model, train, test, K=10)
    print('precision at k:', p_at_k)
    print('mean average precision at k:', m_at_k)

    return p_at_k, m_at_k


def recommend(user_id):
    '''recommend N items to user'''
    sparse_user_item = load_npz("/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/sparse_user_item.npz")

    with open('/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/model.sav', 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    recommended, _ = zip(*model.recommend(user_id, sparse_user_item))

    return recommended, map_movies(recommended)


def recommend_all_users():
    '''recommend N items to all users'''
    sparse_user_item = load_npz("/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/sparse_user_item.npz")

    with open('/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/model.sav', 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    # numpy array with N recommendations for each user
    # remove first array, because those are the columns
    all_recommended = model.recommend_all(user_items=sparse_user_item, N=10,
        recalculate_user=False, filter_already_liked_items=True)[1:]

    # create a new Pandas Dataframe with user_id, 10 recommendations, for all users
    df = pd.read_csv('/Users/maxmaiberger/Downloads/ml-1m/users.dat', delimiter='::', header=None,
        names=['user_id', 'gender', 'agerange', 'occupation', 'timestamp'], engine='python')
    df = df.drop(['gender', 'agerange', 'occupation', 'timestamp'], axis=1)
    df[['rec1', 'rec2', 'rec3', 'rec4', 'rec5', 'rec6', 'rec7', 'rec8', 'rec9', 'rec10']] = pd.DataFrame(all_recommended)
    df.to_pickle("/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/all_recommended.pkl")

    '''melt dataframe into SQL format for Django model
    melted = df.melt(id_vars=['user_id'], var_name='order', value_name='recommendations',
        value_vars=['rec1', 'rec2', 'rec3', 'rec4', 'rec5', 'rec6', 'rec7', 'rec8', 'rec9', 'rec10'])
    melted['order'] = melted.order.str[3:]
    print(melted.sort_values(by=['user_id', 'order']))
    melted.to_pickle('all_recommended_melted.pkl')
    '''

    return df


def recalculate_user(user_ratings):
    '''adds new user and its liked items to sparse matrix and returns recalculated recommendations'''

    alpha = 40
    m = load_npz('/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/sparse_user_item.npz')
    n_users, n_movies = m.shape
    print(n_users)
    ratings = [alpha for i in range(len(user_ratings))]  # wird alpha hier wirklich verrechnet?

    m.data = np.hstack((m.data, ratings))  # add ratings to data
    m.indices = np.hstack( (m.indices, np.array(user_ratings['movie_id'])) )  # indices sind movies  (alle movie ids die user gerated hat)
    m.indptr = np.hstack((m.indptr, len(m.data)))  # indptr sind user  (ist der index an dem nächste user anfängt)
    m._shape = (n_users + 1, n_movies)
    print(m._shape)

    # recommend N items to new user
    with open('/Users/maxmaiberger/Documents/board-game-recommender/import/Data/test_data_saved/model.sav', 'rb') as pickle_in:
        model = pickle.load(pickle_in)
    recommended, _ = zip(*model.recommend(userid=n_users, user_items=m, recalculate_user=True))

    print(map_movies(recommended))
    return recommended, map_movies(recommended)


def main():
    data = load_data()
    print(data)

    # input machine learning model and needed for calculation on the fly - sparse user-item and item-user matrix
    sparse_user_item, sparse_item_user = sparse_matrices(df=data)
    data_pivot = data.pivot(index='user_id', columns='movie_id', values='rating')


    # mapping for user and games to map back ratings to meta data like title, genre, ...
    unique_game_keys = data.loc[:, 'movie_id'].unique()
    unique_user_keys = data.loc[:, 'user_id'].unique()
    mapped_users = map_users(user_ids=unique_user_keys)
    mapped_movies = map_movies(movie_ids=unique_game_keys)
    print(mapped_movies)

    # what items correlate
    #most_similar_items()
    #most_similar_users()

    # build model
    model()

    # recommend items to one or all user in our dataset
    user_rec = recommend(user_id=1)
    users_rec = recommend_all_users()
    print(user_rec)
    print(users_rec)

    if False:
        # recommend on the fly
        # require sparse_user_item matrix
        user_ratings = pd.DataFrame({'user_id': [119911, 119911, 119911, 119911, 119911],  # braucht man eigentlich nicht
                                     'movie_id': [1, 2, 3, 4, 5],
                                     'rating': [4, 5, 4, 3, 1]})

        recalculate_user(user_ratings=user_ratings)


if __name__ == "__main__":
    main()
