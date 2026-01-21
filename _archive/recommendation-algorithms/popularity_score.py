import pandas as pd


def create_num_rating_col(data):
    '''
    function will calculate column with the total number of ratings per game. The column will be added to data.
    '''

    # add number of ratings
    data['total_num_ratings'] = data['bgg_num_user_ratings'] + data['bga_num_user_ratings']
    del data['bgg_num_user_ratings']
    del data['bga_num_user_ratings']
    return data


def create_avg_rating_col(data):
    '''
    function will calculate the average rating per game.
    '''

    # take bgg average rating as total average because platform much bigger than bga
    data['total_avg_ratings'] = data['bgg_average_user_rating']
    del data['bgg_average_user_rating']
    return data


def calculate_popularity_measure(data):
    '''
    function will calculate the popularity measure by normalizing the total number of ratings and average ratings for
    each game. The normalized values will be added together to create a score. The game with the highest score is the
    most popular one.
    '''

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
    '''
    function to get the best n games of the sorted popularity score dataset.
    '''

    best_n_games = data[['game_key', 'name']][:n]
    return best_n_games.to_dict(orient="records")


def popular_games(data: pd.DataFrame, num_recommendations: int = 50):
    '''
    popularity score:
    this function is the main function for the popularity score. The following steps are performed in this function:

    1. calculate total ratings per game
    2. calculate average rating per game
    3. normalize total ratings and average rating per game and add them together per game
    4. sort added values and highest score is most popular game
    '''

    # create new total ratings column
    data = create_num_rating_col(data=data)
    # create new average rating column
    data = create_avg_rating_col(data=data)
    # calculate measure
    data = calculate_popularity_measure(data=data)
    # return highest n games to frontend
    return get_best_n_games(data=data, n=num_recommendations)
