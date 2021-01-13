import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def global_average_prediction(data):
    calculation_data = data.replace(0, np.NaN)
    global_average = calculation_data.mean()

    print('--- global mean: ', global_average)
    return global_average
