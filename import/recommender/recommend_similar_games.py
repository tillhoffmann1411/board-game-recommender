import pandas as pd
import numpy as np


def get_data():
    # get games
    data_games = pd.read_csv('../Data/Joined/Results/BoardGames.csv',
                             usecols=['game_key', 'name', 'min_players', 'max_players',
                                      'min_playtime', 'max_playtime'], index_col=False)
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


def create_mean_best_n_games(data_games, user_id):
    # get best n rated games of user

    data_user = pd.read_csv('../Data/Joined/Results/Reviews.csv', usecols=['user_key', 'game_key', 'rating'],
                            sep=',', header=0)
    data_user = data_user[data_user['user_key'] == user_id]
    # get min rating of best games
    data_user = data_user.sort_values('rating', ascending=False, ignore_index=True)
    min_rating = data_user['rating'][5]
    # get all games with equal or higher rating
    best_n_games = data_user[data_user['rating'] >= min_rating]

    # get details of best rated games
    best_n_games = data_games[data_games['game_key'].isin(list(best_n_games['game_key']))]
    # calculate mean best game
    mean_best_games = best_n_games.iloc[:, 2:].mean(axis=0)

    return mean_best_games


def get_cosine_similarity(x, y):
    numerator = np.dot(x, y)
    denominator = np.linalg.norm(x) * np.linalg.norm(y)

    # x and y must be non-zero vectors
    if denominator > 0:
        sim = numerator / denominator
    else:
        sim = 0

    return sim


def get_recommendation(data_games, mean_best_games):
    # append mean game to all games df
    mean_best_games = pd.DataFrame(mean_best_games).transpose()
    mean_best_games['name'] = 'mean_best_n_games'
    mean_best_games['game_key'] = 0
    data_games = data_games.append(mean_best_games, ignore_index=True)

    # get mean item
    index = data_games[data_games['name'] == 'mean_best_n_games'].index
    query_item = data_games.iloc[index, 2:]
    query_item = query_item.to_numpy()

    # compute cosine similarities
    similarities = []
    for i in range(len(data_games['name'])):

        # skip the query item
        if i != index:
            # iterate over items
            other_item = data_games.iloc[i, 2:]
            other_item = other_item.to_numpy()

            # compute cosine similarity between both items
            sim = get_cosine_similarity(query_item, other_item)

            # save results on list
            similarities.append((data_games['name'][i], sim))

    # sort pairs
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

    return sorted_similarities


def main():
    # get data
    game_data, category_data, mechanics_data = get_data()

    # prepare data - one hot encode
    df = prepare_data(data_games=game_data, data_category=category_data, data_mechanics=mechanics_data)

    # get user id - frontend
    user_id = 195001

    # create mean of best rated games
    mean_best_games = create_mean_best_n_games(data_games=df, user_id=user_id)

    # calculate similarity
    similarities = get_recommendation(data_games=df, mean_best_games=mean_best_games)

    print(similarities)


if __name__ == '__main__':
    main()
