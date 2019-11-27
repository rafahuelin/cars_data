import pandas as pd
import os
from pathlib import Path
from sqlalchemy import create_engine

dbs_folder = r'D:\Projects\Python\cars_data\extract'


def create_db_list():
    dbs_files = sorted(Path(dbs_folder).glob('*.db'))
    dbs_list = [db.name for db in dbs_files]
    return dbs_list


def add_databases_to_dataframe(dbs_list):
    df_list = []
    for i, db in enumerate(dbs_list):
        current_engine = create_engine(f'sqlite:///{db}')
        current_df = pd.read_sql('cars', current_engine)
        df_list.append(current_df)

    merged_df = pd.concat(df_list)
    merged_df = merged_df.drop_duplicates()
    print(len(merged_df.index))
    return merged_df


def export_db(merged_df):
    engine = create_engine('sqlite:///merged_idae_complete.db')
    merged_df.to_sql('cars', engine, index=False)


def main():
    dbs_list = create_db_list()
    merged_df = add_databases_to_dataframe(dbs_list)
    export_db(merged_df)


if __name__ == '__main__':
    main()
