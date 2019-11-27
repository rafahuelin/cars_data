import pandas as pd
from sqlalchemy import create_engine

filename = 'ES.txt'  # data originally from "http://www.geonames.org/"

df = pd.read_csv(filename, sep='\t')
df.columns = ["Country_code", "Postal_code", "City", "Region", "Region_code", "Province", "Province_code", "d1", "d2", "latitude", "longitude", "accuracy"]
df = df.drop(['d1', 'd2'], axis=1)

engine = create_engine('sqlite:///cars_data.db')
df.to_sql('zip_codes', engine)
