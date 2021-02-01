import pandas as pd
import numpy as np
import time


def get_data():
    # get games
    data_games = pd.read_csv('../Data/Joined/Results/BoardGames.csv',
                             usecols=['game_key', 'name', 'min_players', 'max_players',
                                      'min_playtime', 'max_playtime', 'bgg_average_weight'], index_col=False)
    # get game characteristics
    data_category = pd.read_csv('../Data/Joined/Results/Category_Game_Relation.csv', usecols=['game_key', 'category_key'])
    # get game mechanics
    data_mechanics = pd.read_csv('../Data/Joined/Results/Mechanic_Game_Relation.csv', usecols=['game_key', 'mechanic_key'])

    return data_games, data_category, data_mechanics


def prepare_data(data_games, data_category, data_mechanics):
    # prepare data
    max_mec_key = max(data_mechanics['mechanic_key'])
    data_mechanics['mechanic_key'] = 'mec_' + data_mechanics['mechanic_key'].astype(str)
    max_cat_key = max(data_category['category_key'])
    data_category['category_key'] = 'cat_' + data_category['category_key'].astype(str)

    # fill missing values with mean
    data_games['min_players'] = data_games['min_players'].fillna(data_games['min_players'].mean())
    data_games['max_players'] = data_games['max_players'].fillna(data_games['max_players'].mean())
    data_games['min_playtime'] = data_games['min_playtime'].fillna(data_games['min_playtime'].mean())
    data_games['max_playtime'] = data_games['max_playtime'].fillna(data_games['max_playtime'].mean())
    data_games['bgg_average_weight'] = data_games['bgg_average_weight'].fillna(data_games['bgg_average_weight'].mean())

    # merge data
    data_category = (data_category.groupby('game_key')['category_key'].apply(lambda x: list(set(x))).reset_index())
    data_mechanics = (data_mechanics.groupby('game_key')['mechanic_key'].apply(lambda x: list(set(x))).reset_index())
    data_games = data_games.merge(data_category, left_on='game_key', right_on='game_key')
    data_games = data_games.merge(data_mechanics, left_on='game_key', right_on='game_key')
    data_games['category_key'] = [','.join(map(str, l)) for l in data_games['category_key']]
    data_games['mechanic_key'] = [','.join(map(str, l)) for l in data_games['mechanic_key']]

    # one hot encode cat and mec
    game_category_characteristics = list(range(max_cat_key))
    game_category_characteristics = ['cat_' + str(elem) for elem in game_category_characteristics]
    game_mechanic_characteristics = list(range(max_mec_key))
    game_mechanic_characteristics = ['mec_' + str(elem) for elem in game_mechanic_characteristics]
    for cat in game_category_characteristics:
        data_games[cat] = data_games['category_key'].apply(extract_category, args=(cat,))
    for mec in game_mechanic_characteristics:
        data_games[mec] = data_games['mechanic_key'].apply(extract_category, args=(mec,))

    # delete useless columns
    del data_games['category_key']
    del data_games['mechanic_key']

    return data_games


def extract_category(categories, cat):
    print('one hot encode for:', cat)

    # categories without values
    if pd.isna(categories):
        return 0

    # split list and
    categories_list = categories.split(",")
    if cat in categories_list:
        return 1
    else:
        return 0


def create_bool_cat_and_mec(data):
    # manipulate categories
    n_values_to_change_cat = 4  # number of categories a mean game
    data.iloc[-1:, 7:137] = data.iloc[-1:, 7:137].\
        mask(data.iloc[-1:, 7:137].
             rank(axis=1, method='min', ascending=False) > n_values_to_change_cat, 0).astype(bool).astype(int)

    # manipulate mechanics
    n_values_to_change_mec = 4  # number of mechanics a mean game
    data.iloc[-1:, 138:] = data.iloc[-1:, 138:].\
        mask(data.iloc[-1:, 138:].
             rank(axis=1, method='min', ascending=False) > n_values_to_change_mec, 0).astype(bool).astype(int)

    return data


def create_mean_best_n_games(data_games, user_id):
    # get best n rated games of user - here frontend can only query data from user of interest
    data_user = pd.read_csv('../Data/Joined/Results/Reviews.csv', usecols=['user_key', 'game_key', 'rating'],
                            sep=',', header=0)
    data_user = data_user[data_user['user_key'] == user_id]
    # get already rated games
    already_rated_games = data_user['game_key'].to_list()
    # get min rating of best games
    data_user = data_user.sort_values('rating', ascending=False, ignore_index=True)
    min_rating = data_user['rating'][0]
    # get all games with equal or higher rating
    best_n_games = data_user[data_user['rating'] >= min_rating]

    # get details of best rated games
    best_n_games = data_games[data_games['game_key'].isin(list(best_n_games['game_key']))]
    # calculate mean best game
    mean_best_games = best_n_games.iloc[:, 2:].mean(axis=0)

    return mean_best_games, already_rated_games


def get_cosine_similarity(x, y, weights):
    '''  x and y are numpy arrays with values of query item and other item '''
    # only compare nonzero values from query game - otherwise games will be similar because most features are 0
    # get indices of zero values in query game
    #zero_indices = np.where(x == 0)[0]
    #x = np.delete(x, zero_indices)
    #y = np.delete(y, zero_indices)

    # calculate weighted features
    x = x * weights
    y = y * weights

    # calculate cosine similarity
    numerator = np.dot(x, y)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)

    # x and y must be non-zero vectors
    if denominator > 0:
        sim = numerator / denominator
    else:
        sim = 0

    return sim


def get_recommendations(data_games, mean_best_games, already_rated_games):
    # append mean game to all games df
    mean_best_games = pd.DataFrame(mean_best_games).transpose()
    mean_best_games['name'] = 'mean_best_n_games'
    mean_best_games['game_key'] = 0
    data_games = data_games.append(mean_best_games, ignore_index=True)

    # only select n best categories and mechanics
    data_games = create_bool_cat_and_mec(data=data_games)

    # normalize columns which are not normalized yet
    data_games.iloc[:, 2:7] = data_games.iloc[:, 2:7].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

    # get mean item
    index = data_games[data_games['name'] == 'mean_best_n_games'].index
    query_game = data_games.iloc[index, 2:]
    query_game = query_game.to_numpy()[0]

    # create weight vector - weights should add up to 1
    weight_number_players = 0.1
    weight_time = 0.1
    weight_game_difficulty = 0.1
    weight_cat = 0.5
    weight_mec = 0.2
    weights = np.array([weight_number_players/2]*2 + [weight_time/2]*2 + [weight_game_difficulty/1]*1 + \
              [weight_cat/131]*131 + [weight_mec/229]*229)

    # compute cosine similarities
    similarities = []
    for i in range(len(data_games['name'])):

        # skip the query game
        if i != index:
            # iterate over games
            other_game = data_games.iloc[i, 2:]
            other_game = other_game.to_numpy()

            # compute cosine similarity between both games
            sim = get_cosine_similarity(query_game, other_game, weights)

            # dont save already rated games
            if data_games['game_key'][i] not in already_rated_games:
                # save results on list
                similarities.append((data_games['game_key'][i], data_games['name'][i], sim))

    # sort pairs
    sorted_similarities = sorted(similarities, key=lambda x: x[2], reverse=True)

    return sorted_similarities


def main():

    ## get data
    #game_data, category_data, mechanics_data = get_data()

    ## prepare data - one hot encode
    #df = prepare_data(data_games=game_data, data_category=category_data, data_mechanics=mechanics_data)

    # save data
    #df.to_csv('/Users/maxmaiberger/Downloads/one_hot_df.csv', index=False)
    # get saved data
    df = pd.read_csv('/Users/maxmaiberger/Downloads/one_hot_df.csv')

    # get user id - frontend
    user_id = 195001  # 121709 - few games  # 195001 - many games
    # create mean of best rated games
    mean_best_games, already_rated_games = create_mean_best_n_games(data_games=df, user_id=user_id)
    start_time = time.time()

    # calculate similarity
    similarities = get_recommendations(data_games=df, mean_best_games=mean_best_games,
                                       already_rated_games=already_rated_games)
    print(similarities)
    end_time = time.time()
    print(end_time-start_time)


if __name__ == '__main__':
    main()
