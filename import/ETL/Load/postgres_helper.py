import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
import io
import logging
import math
from datetime import datetime


def split_df_in_batches(df, batchsize):
    num_batches = math.ceil(len(df) / batchsize)
    return np.array_split(df, num_batches)


class PostgresWrapper:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        # probing connection for validity
        self.connection = self.connect()

        print("Initial connection probing successful")
        self.disconnect()

    def connect(self) -> psycopg2._psycopg.connection:
        print("Connecting to " + self.host + "...")
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

        return conn

    def disconnect(self):
        self.connection.cursor().close()
        # self.connection = None

    def execute_query(self, query: str):
        if not self.connection:
            self.connect()
        cur = self.connection.cursor()
        cur.execute(query)
        return cur.fetchall()

    def df_to_csv_string(self, df: pd.DataFrame):
        if 'description' in df.columns:
            df['description'] = df['description'].replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True)
        csv_df = io.StringIO()
        for row in df.values:
            csv_df.write("\t".join(map(str, row)) + '\n')
        csv_df.seek(0)
        return csv_df

    def upload_dataframe(self, table: str, df: pd.DataFrame, batchsize: int = -1, truncate_table: bool = False,
                         commit: bool = False, start_batch: int = 0):
        assert isinstance(table, str)
        assert isinstance(df, pd.DataFrame)
        assert isinstance(batchsize, int)
        assert isinstance(truncate_table, bool)
        assert isinstance(commit, bool)

        if truncate_table:
            print("delete rows from " + table + "...")
            with self.connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE ' + table + ' CASCADE;')

        if batchsize != -1:
            print('Use batch strategy with batchsize ' + str(batchsize))
            t_start = datetime.now()
            # Split dataframe into batches and create new one
            df_batches = split_df_in_batches(df, batchsize)
            if start_batch != 0:
                del df_batches[0:start_batch]
            print('Number of rows: ' + str(len(df)) + ' - Number of Batches: ' + str(len(df_batches)))

            for idx, df_batch in enumerate(df_batches):
                t_batch_start = datetime.now()
                # Create csv like string out of one batch
                csv_df = self.df_to_csv_string(df_batch)

                with self.connection.cursor() as cursor:
                    # copy csv like string to table
                    cursor.execute("SET CLIENT_ENCODING TO 'UTF8';")
                    cursor.copy_from(csv_df,
                                     table,
                                     sep="\t",
                                     columns=['"' + item + '"' for item in df.columns],
                                     null="")
                    t_batch_end = datetime.now()
                    print('Time for ' + str(idx) + '. batch: ' + str((t_batch_end - t_batch_start).total_seconds()))
                    if commit:
                        self.connection.commit()
                        logging.debug("data successfully inserted")
                    else:
                        return self.connection

            t_end = datetime.now()
            print('Total time for ' + table + ' import: ' + str((t_end - t_start).total_seconds()))

        else:
            print('Number of rows: ' + str(len(df)))
            csv_df = self.df_to_csv_string(df)

            with self.connection.cursor() as cursor:
                cursor.copy_from(csv_df,
                                 table,
                                 sep="\t",
                                 columns=['"' + item + '"' for item in df.columns],
                                 null="")
                if commit:
                    self.connection.commit()
                    logging.debug("data successfully inserted")
                else:
                    return self.connection
