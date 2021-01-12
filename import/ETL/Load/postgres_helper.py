import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
import io
import logging
import math


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
        # self.connection.cursor = self.connection.cursor()
        print("Initial connection probing successful")
        self.disconnect()

    def connect(self) -> psycopg2._psycopg.connection:
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

    def upload_dataframe(self, table: str, df: pd.DataFrame, batchsize: int = -1, truncate_table: bool = False, commit: bool = False):
        assert isinstance(table, str)
        assert isinstance(df, pd.DataFrame)
        assert isinstance(batchsize, int)
        assert isinstance(truncate_table, bool)
        assert isinstance(commit, bool)

        with self.connection.cursor() as cursor:
            if truncate_table:
                logging.debug("delete rows from " + table + "...")
                cursor.execute(
                    'TRUNCATE TABLE ' + table + ' CASCADE;')

        if batchsize != -1:

            df_batches = split_df_in_batches(df, batchsize)

            for batch in df_batches:
                csv_file_like_object = io.StringIO()
                for row in df.values:
                    csv_file_like_object.write("\t".join(map(str, row)) + '\n')
                csv_file_like_object.seek(0)

                with self.connection.cursor() as cursor:
                    cursor.copy_from(csv_file_like_object,
                                     table,
                                     sep="\t",
                                     columns=['"' + item + '"' for item in df.columns],
                                     null="")
                    if commit:
                        self.connection.commit()
                        logging.debug("data successfully inserted")
                    else:
                        logging.debug("something went wrong!")
                        return self.connection

        else:
            csv_file_like_object = io.StringIO()
            for row in df.values:
                csv_file_like_object.write("\t".join(map(str, row)) + '\n')
            csv_file_like_object.seek(0)

            with self.connection.cursor() as cursor:
                cursor.copy_from(csv_file_like_object,
                                 table,
                                 sep="\t",
                                 columns=['"' + item + '"' for item in df.columns],
                                 null="")
                if commit:
                    self.connection.commit()
                    logging.debug("data successfully inserted")
                else:
                    return self.connection


