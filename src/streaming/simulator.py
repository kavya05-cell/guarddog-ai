import pandas as pd

def stream_records(dataset_path):
    data = pd.read_csv(dataset_path).sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    for _, row in data.iterrows():
        yield row.where(pd.notna(row), None).to_dict()