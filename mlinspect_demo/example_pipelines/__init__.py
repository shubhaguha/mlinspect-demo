import os

import pandas as pd

from mlinspect.utils import get_project_root


healthcare_filename = os.path.join(get_project_root(), "example_pipelines",
                                   "healthcare", "healthcare.py")
adult_filename = os.path.join(get_project_root(), "example_pipelines",
                              "adult_demo", "adult_demo.py")
with open(healthcare_filename) as healthcare_file:
    healthcare_pipeline = healthcare_file.read()
with open(adult_filename) as adult_file:
    adult_pipeline = adult_file.read()


histories = pd.read_csv(
    os.path.join(get_project_root(), "example_pipelines", "healthcare", "histories.csv"),
    na_values='?')
patients = pd.read_csv(
    os.path.join(get_project_root(), "example_pipelines", "healthcare", "patients.csv"),
    na_values='?')
HEALTHCARE_DATA = patients.merge(histories, on=['ssn'])
ADULT_DATA = pd.read_csv(
    os.path.join(get_project_root(), "example_pipelines", "adult_demo", "train.csv"),
    na_values='?', index_col=0)
