from pathlib import Path

import pandas as pd


HEALTHCARE_PATH = Path(__file__).parent / "healthcare"
ADULT_PATH = Path(__file__).parent / "adult"


# Pipeline definitions
with (HEALTHCARE_PATH / "healthcare.py").open() as healthcare_file:
    HEALTHCARE_PIPELINE = healthcare_file.read()

with (ADULT_PATH / "adult.py").open() as adult_file:
    ADULT_PIPELINE = adult_file.read()


# Datasets
histories = pd.read_csv(HEALTHCARE_PATH / "histories.csv", na_values='?')
patients = pd.read_csv(HEALTHCARE_PATH / "patients.csv", na_values='?')
HEALTHCARE_DATA = patients.merge(histories, on=['ssn'])

ADULT_DATA = pd.read_csv(ADULT_PATH / "train.csv", na_values='?', index_col=0)
