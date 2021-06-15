from importlib.resources import read_text, path

import pandas as pd


HEALTHCARE_PIPELINE = read_text(__name__, "healthcare.py")

with path(__name__, "patients.csv") as patients_path:
    patients = pd.read_csv(patients_path, na_values='?')

with path(__name__, "histories.csv") as histories_path:
    histories = pd.read_csv(histories_path, na_values='?')

HEALTHCARE_DATA = patients.merge(histories, on=['ssn'])
