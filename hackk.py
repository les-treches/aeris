import pandas as pd
import os

folder = r"C:\Users\sridh\Desktop\hackathon"

files = [
    "india_forecast.csv",
    "region_forecast.csv"
]

for file in files:

    path = os.path.join(folder, file)

    print("\n" + "=" * 80)
    print("FILE:", file)
    print("=" * 80)

    # Load CSV
    df = pd.read_csv(path)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

