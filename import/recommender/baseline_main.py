# This script was used to create a baseline for our following recommender approaches. For the baseline 3 different
# pipelines exist:
#   1. preparation_pipeline
#       - get raw data
#       - prepare data
#       - split data (train, test)
#   2. modeling_pipeline
#       - chose one of the 3 approaches (global_average, user_average, game_average)
#       - calculate predictions
#   3. evaluation_pipeline
#       - evaluate predictions
#
# To get deeper insights have a look at our function descriptions.


from baseline_preparation import *
from baseline_modeling import *
from baseline_evaluation import *


def preparation_pipeline():
    '''
    This function will call preparation functions to get the recommendation data and prepare it.
    '''

    # get data from database
    df = get_recommendation_data(link='../Data/Joined/Results/Reviews.csv',  # link to data
                                 min_number_ratings_game=500,  # filter games
                                 min_number_ratings_user=5,  # filter user
                                 size_user_sample=100_000,  # create sample
                                 seed=None)  # None for random, int for comparison

    # prepare data
    df = prepare_data(data=df)

    # split data
    data_split = make_train_test_split(data=df,
                                       test_size=0.2,
                                       seed=42)

    return data_split


def modeling_pipeline(df, global_average, game_average, user_average):
    '''
    This function will take the before prepared data and call some functions from the modeling pipeline to predict new
    games. The output will be a dict with the added predictions.

    df: data form preparation pipeline
    global_average: TRUE if you want to calculate global average as prediction, else FALSE
    game_average: TRUE if you want to calculate game average as prediction, else FALSE
    user_average: TRUE if you want to calculate user average as prediction, else FALSE

    Only one argument can be set to TRUE.
    '''

    # get data from dict
    data_train = df['train_data']
    data_original = df['original_data']
    delete_position = df['delete_position']

    # prediction methods
    if global_average:
        pred = global_average_prediction(data=data_train)
    elif game_average:
        pred = game_average_prediction(data=data_train)
    elif user_average:
        pred = user_average_prediction(data=data_train)
    else:
        print('You have to choose a model')

    # create dict for return
    info = {'train_data': data_train,
            'original_data': data_original,
            'delete_position': delete_position,
            'prediction': pred}

    return info


def evaluation_pipeline(result):
    '''
    This function will call the evaluation pipeline. Input is the dict with the information which was collected in the
    steps before.
    '''

    calculate_rmse(result)


if __name__ == "__main__":
    # prepataion
    data = preparation_pipeline()
    # modeling
    result = modeling_pipeline(df=data,
                               global_average=False,
                               game_average=True,
                               user_average=False)
    # evaluation
    evaluation_pipeline(result=result)
