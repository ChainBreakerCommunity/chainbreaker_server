# ==============================================================================
# Copyright 2020 The Chain Breaker Authors. All Rights Reserved.
# ==============================================================================

"""
MySQL Service
"""
from sqlalchemy import create_engine, MetaData
import pandas as pd

class SQLService:
    def __init__(self, database,
                 user,
                 password,
                 server,
                 dialect="mysql",
                 port=3306):
        self.database = database
        self.user = user
        self.password = password
        self.dialect = dialect
        self.server = server
        self.port = port
        try:
            self.engine, self.metadata = self.get_engine_and_metadata()
            self.success = True
        except:
            self.success = False

    def get_engine_and_metadata(self):
        command = f"{self.dialect}://{self.user}:{self.password}@{self.server}:{self.port}/{self.database}?charset=utf8mb4"
        engine = create_engine(command)
        metadata = MetaData()
        metadata.reflect(engine)
        return engine, metadata

    def df_from_query(self, query):
        df = pd.read_sql(query, self.engine)
        return df

    def insert_record(self, table, record):
        #print(record)
        table = self.metadata.tables[table]
        #try:
        with self.engine.begin() as connection:
            record = tuple(record)
            connection.execute(table.insert().values(record))

    def update_record(self, table, column_name_where, value_where, dictionary_values):
        table = self.metadata.tables[table]
        with self.engine.begin() as connection:
            connection.execute(table.update().where(table.columns[column_name_where]==value_where).values(dictionary_values))

    def destroy(self):
        self.engine.dispose()

    def success(self):
        return self.success
