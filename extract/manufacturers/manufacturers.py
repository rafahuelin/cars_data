import camelot
import pandas as pd
from sqlalchemy import create_engine


columns = [
    'manufacturer',
    'model',
    'sales term',
    'cc',
    'cylinders',
    'fuel',
    'kW',
    'cvf',
    'HP',
    'value €'
]

engine = create_engine('sqlite:///boe_cars.db')
df = pd.DataFrame(None, columns=columns)
df = pd.DataFrame()

for i in range(4, 609):
    table = camelot.read_pdf('BOE-A-2018-17664.pdf', pages=f'{i}')
    current_df = table[0].df.iloc[2:]
    df = df.append(current_df)
   
    print(i, current_df.tail(1), df.tail(1))
    if i % 2 == 0:
        df.to_sql('cars', engine, if_exists='replace', index=False)
        # df.to_csv('boe_manufacturers.csv')

df.to_sql('cars', engine, if_exists='replace', index=False)
