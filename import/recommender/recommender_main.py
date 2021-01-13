from data_preparation import *
from data_modeling import *
from evaluation import *


def preparation_pipeline():
    # get data from database
    df = get_recommendation_data(link='../Data/Joined/Results/Reviews.csv',
                                 sample_number_rows=5000,
                                 random_state=41)  # default value is None

    # prepare data
    df = prepare_data(data=df,
                      min_number_ratings_user=0,
                      min_number_ratings_game=0,
                      fill=0)

    # split data
    split_data = make_train_test_split(data=df,
                                       train_size=0.8,
                                       test_size=0.2,
                                       seed=42)

    return split_data


def modeling_pipeline(df):
    # get new user name for recommendation
    new_user = "Artax"  # "4Corners"  # from frontend?

    # get data from dict
    train_data = df['train_data']
    delete_position = df['delete_position']

    bla = global_average_prediction(data=train_data)


def evaluation_pipeline():
    print("is missing")


if __name__ == "__main__":
    data = preparation_pipeline()
    modeling_pipeline(df=data)
    evaluation_pipeline()


