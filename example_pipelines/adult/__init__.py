from importlib.resources import read_text, path

import pandas as pd


ADULT_PIPELINE = read_text(__name__, "adult.py")

with path(__name__, "train.csv") as train_path:
    ADULT_DATA = pd.read_csv(train_path, na_values='?', index_col=0)
