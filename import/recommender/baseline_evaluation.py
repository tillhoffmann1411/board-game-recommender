from sklearn.metrics import mean_squared_error
from math import sqrt


def calculate_rmse(result):
    '''
    This function will calculate the mse and rmse of the before used approach.
    '''

    # get data from dict
    data_prediction = result['prediction']
    data_original = result['original_data']
    delete_position = result['delete_position']

    # get ratings we want to compare (original and predicted)
    values_original = []
    values_predicted = []
    for x, y in delete_position:
        values_original.append(data_original.loc[x, y])
        values_predicted.append(data_prediction.loc[x, y])

    # calculate rmse
    mse = mean_squared_error(y_true=values_original, y_pred=values_predicted)
    rmse = sqrt(mse)

    print("---mse: ", mse)
    print("---rmse: ", rmse)
