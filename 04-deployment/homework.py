import sys
import pickle
import pandas as pd

def load_model():
    with open('model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)
    return dv, model


categorical = ['PULocationID', 'DOLocationID']
def read_data(filename):
    df = pd.read_parquet(filename)
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df

def predict(df, dv, model):
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)
    return y_pred



def export_data(df, y_pred, year, month):
    df_result = pd.DataFrame()
    df_result['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    df_result['predicted_duration'] = y_pred
    output_file = f'yellow_tripdata_{year:04d}-{month:02d}_predicted.parquet'
    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )


def run():
    if len(sys.argv) < 2:
        print("[!] Please specify year and month ")
        print("SYNTAX: python starter.py [YEAR] [MONTH] ")
        sys.exit(1)

    #taxi_type = sys.argv[1]  #yellow
    year = int(sys.argv[1]) # 2023
    month = int(sys.argv[2]) # 3

    print("Loading model...")
    dv, lr = load_model()

    print("Reading data...")
    df = read_data(f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet')

    print("Predicting trip duration...")
    y_pred = predict(df, dv, lr)

    print(f"Predicted mean duration {y_pred.mean()}")

    print("Exporting data...")
    export_data(df, y_pred, year, month)


if __name__ == '__main__':
    run()