"""Predicting which adults have an annual income greater than 50K USD."""
import pandas as pd
import numpy as np
from sklearn.preprocessing import label_binarize
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

train_data = pd.read_csv("example_pipelines/adult/train.csv", na_values='?', index_col=0)
test_data = pd.read_csv("example_pipelines/adult/test.csv", na_values='?', index_col=0)

#train_data = train_data[train_data['native-country'].notna()]
#train_data = train_data[train_data['occupation'].notna()]
#train_data = train_data[train_data['age'] > 40]
#train_data = train_data[train_data['education-num'] >= 10]
#train_data = train_data[train_data['marital-status'] == 'Married-civ-spouse']
#train_data = train_data[train_data['capital-gain'] > 0]
#train_data = train_data[train_data['native-country'].notna() & train_data['income-per-year'].notna()]
train_data = train_data.dropna()
test_data = test_data.dropna()

train_labels = label_binarize(train_data['income-per-year'], classes=['>50K', '<=50K'])
test_labels = label_binarize(test_data['income-per-year'], classes=['>50K', '<=50K'])

nested_categorical_feature_transformation = Pipeline([
        ('impute', SimpleImputer(missing_values=np.nan, strategy='most_frequent')),  # Try dropna/comment out imputer
        ('encode', OneHotEncoder(handle_unknown='ignore'))
    ])

nested_feature_transformation = ColumnTransformer(transformers=[
        ('categorical', nested_categorical_feature_transformation, ['education', 'workclass']),
        ('numeric', StandardScaler(), ['age', 'hours-per-week'])  # change columns, e.g. education-num instead of educ.
    ])

nested_income_pipeline = Pipeline([
    ('features', nested_feature_transformation),
    ('classifier', DecisionTreeClassifier())])

nested_income_pipeline.fit(train_data, train_labels)

print("Mean train accuracy:", nested_income_pipeline.score(train_data, train_labels))
print("Mean test accuracy:", nested_income_pipeline.score(test_data, test_labels))  # Use separate test set + load additional file or not