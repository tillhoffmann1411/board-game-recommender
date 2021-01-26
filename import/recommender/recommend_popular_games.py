import pandas as pd


def get_data(link):
    # get games
    data_games = pd.read_csv('../Data/Joined/Results/BoardGames.csv',
                             usecols=['game_key', 'name', 'bgg_num_user_ratings', 'bga_num_user_ratings',
                                      'bgg_average_user_rating'], index_col=False)
    return data_games


def create_num_rating_col(data):
    # add number of ratings
    data['total_num_ratings'] = data['bgg_num_user_ratings'] + data['bga_num_user_ratings']
    del data['bgg_num_user_ratings']
    del data['bga_num_user_ratings']

    return data


def create_avg_rating_col(data):
    # take bgg average rating as total average because platform much bigger than bga
    data['total_avg_ratings'] = data['bgg_average_user_rating']
    del data['bgg_average_user_rating']

    return data


def calculate_popularity_measure(data):
    # normalize number ratings and rating
    data['normalized_num'] = (data['total_num_ratings']-data['total_num_ratings'].min())/\
                                   (data['total_num_ratings'].max()-data['total_num_ratings'].min())
    data['normalized_avg'] = (data['total_avg_ratings']-data['total_avg_ratings'].min())/\
                                   (data['total_avg_ratings'].max()-data['total_avg_ratings'].min())

    # create popularity measurement
    data['popularity_measurement'] = data['normalized_avg'] + data['normalized_num']

    # sort games by number of all ratings
    data = data.sort_values('popularity_measurement', ascending=False)

    return data


def get_best_n_games(data, n):
    best_n_games = data[['game_key', 'name']][:n]

    return best_n_games


if __name__ == '__main__':
    df = get_data(link='../Data/Joined/Results/BoardGames.csv')
    df = create_num_rating_col(data=df)
    df = create_avg_rating_col(data=df)
    df = calculate_popularity_measure(data=df)
    res = get_best_n_games(data=df, n=100)
    print('done')
