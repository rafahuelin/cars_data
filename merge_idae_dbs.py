import pandas as pd
import os
from pathlib import Path
from sqlalchemy import create_engine

os.chdir('idae_dbs')
dbs_folder = r'D:\Projects\Python\cars_data\idae_dbs'
# result_engine = create_engine('sqlite:///merged_idae.db')


def create_db_list():
    dbs_files = sorted(Path(dbs_folder).glob('*.db'))
    dbs_list = [db.name for db in dbs_files]
    return dbs_list


def add_databases_to_dataframe(dbs_list):
    # df = pd.DataFrame()
    for i, db in enumerate(dbs_list):
        current_engine = create_engine(f'sqlite:///{db}')
        current_df = pd.read_sql('cars', current_engine)
        # print(df, '---', f'{current_df.index}')
        if i == 0:
            df = current_df
        else:
            df.append(current_df)
            print('else')
        print(len(current_df.index), '---', len(df.index))

    print(len(df.index))


def main():
    dbs_list = create_db_list()
    add_databases_to_dataframe(dbs_list)


if __name__ == '__main__':
    main()
