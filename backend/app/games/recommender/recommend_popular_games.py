import pandas as pd


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
    data['normalized_num'] = (data['total_num_ratings']-data['total_num_ratings'].min()) /\
        (data['total_num_ratings'].max()-data['total_num_ratings'].min())
    data['normalized_avg'] = (data['total_avg_ratings']-data['total_avg_ratings'].min()) /\
        (data['total_avg_ratings'].max()-data['total_avg_ratings'].min())

    # create popularity measurement
    data['popularity_measurement'] = data['normalized_avg'] + data['normalized_num']

    # sort games by number of all ratings
    data = data.sort_values('popularity_measurement', ascending=False)
    return data


def get_best_n_games(data, n):
    best_n_games = data[['game_key', 'name']][:n]
    return best_n_games.to_dict(orient="records")


def popular_games(data: pd.DataFrame, num_recommendations: int = 50):
    data = create_num_rating_col(data=data)
    data = create_avg_rating_col(data=data)
    data = calculate_popularity_measure(data=data)
    return get_best_n_games(data=data, n=num_recommendations)
