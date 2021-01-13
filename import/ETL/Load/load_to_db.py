from ETL.Load.postgres_helper import PostgresWrapper
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import logging
import os

env_path = Path('../../../.env')
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


    # create instance of Postgres Wrapper:
    dbWrapper = PostgresWrapper(host=os.getenv('POSTGRES_HOST'),
                                user=os.getenv('POSTGRES_USER'),
                                password=os.getenv('POSTGRES_PASSWORD'),
                                database=os.getenv('POSTGRES_DB'),
                                port=os.getenv('POSTGRES_PORT'))

    dbWrapper.connect()

    # execute upload
    dbWrapper.upload_dataframe(table='accounts_usertaste',
                               df=users_df,
                               batchsize=100,
                               truncate_table=True,
                               commit=True)

    logging.info('Upload completed')
    dbWrapper.disconnect()
    logging.info('Disconnected')
