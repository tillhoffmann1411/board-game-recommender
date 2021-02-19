from data_preparation import *
from data_modeling import *
from evaluation import *


def preparation_pipeline():
    # get data from database
    df = get_recommendation_data(link='../Data/Joined/Results/Reviews.csv',
                                 min_number_ratings_game=500,
                                 min_number_ratings_user=5,
                                 size_user_sample=100_000,
                                 seed=None)  # None for random, int for comparison

    # prepare data
    df = prepare_data(data=df)

    # split data
    data_split = make_train_test_split(data=df,
                                       train_size=0.8,
                                       test_size=0.2,
                                       seed=42)

    return data_split


def modeling_pipeline(df, global_average, game_average, user_average):
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
    calculate_rmse(result)


if __name__ == "__main__":
    data = preparation_pipeline()
    result = modeling_pipeline(df=data,
                               global_average=False,
                               game_average=True,
                               user_average=False)
    evaluation_pipeline(result=result)
