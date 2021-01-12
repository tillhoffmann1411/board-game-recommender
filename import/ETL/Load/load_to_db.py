from ETL.Load.postgres_helper import PostgresWrapper
from dotenv import load_dotenv
import pandas as pd
import logging
import os

load_dotenv()


def upload_users_to_db():

    # import users:
    users_df = pd.read_csv('../Data/Joined/Results/User.csv', index_col=0)

    # rename a few columns:
    users_df.rename(columns={'user_key': 'id',
                             'user_name': 'username',
                             'user_origin': 'origin',
                             'num_ratings': 'number_of_ratings',
                             }, inplace=True)

    # drop avg rating column:
    del users_df['avg_rating']


    # create Postgres Wrapper:
    dbWrapper = PostgresWrapper(host=os.getenv('DATA_DB_HOST'),
                                user=os.getenv('DATA_DB_USER'),
                                password=os.getenv('DATA_DB_PASSWORD'),
                                database=os.getenv('DATA_DB_NAME'),
                                port=os.getenv('DATA_DB_PORT'))

    dbWrapper.connect()


    # execute upload
    dbWrapper.upload_dataframe(table='accounts_usertaste',
                               df=users_df,
                               commit=True,
                               batchsize=-1,
                               truncate_table=False)

    logging.info('Upload completed')
    dbWrapper.disconnect()
    logging.info('Disconnected')
