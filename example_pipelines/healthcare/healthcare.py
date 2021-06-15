"""Predicting which patients are at a higher risk of complications."""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from example_pipelines.healthcare.healthcare_utils import MyW2VTransformer, MyKerasClassifier, \
    create_model

patients = pd.read_csv("example_pipelines/healthcare/patients.csv", na_values='?')
histories = pd.read_csv("example_pipelines/healthcare/histories.csv", na_values='?')

data = patients.merge(histories, on=['ssn'])
complications = data.groupby('age_group') \
    .agg(mean_complications=('complications', 'mean'))
data = data.merge(complications, on=['age_group'])
data['label'] = data['complications'] > 1.2 * data['mean_complications']
# data = data[(data['age_group'] == 'group1') | (data['age_group'] == 'group2')]
data = data[['smoker', 'last_name', 'county', 'num_children', 'race', 'income', 'label']]
data = data[data['county'].isin(['county2', 'county3'])]  # Add or remove this line, modify counties
# data = data[data['race'] == 'race3']

# data = data.dropna()  # Add this line and/or remove the imputer
impute_and_one_hot_encode = Pipeline([
    ('impute', SimpleImputer(strategy='most_frequent')),
    ('encode', OneHotEncoder(sparse=False, handle_unknown='ignore'))  # Test sparse=True
])
featurisation = ColumnTransformer(transformers=[
    ("impute_and_one_hot_encode", impute_and_one_hot_encode,
     ['smoker', 'county', 'race']),  # Remove/add feature columns, e.g., remove race
    ('word2vec', MyW2VTransformer(min_count=2), ['last_name']),
    ('numeric', StandardScaler(), ['num_children', 'income'])
])
neural_net = MyKerasClassifier(build_fn=create_model, epochs=10, batch_size=1, verbose=0)
pipeline = Pipeline([
    ('features', featurisation),
    ('learner', neural_net)])

train_data, test_data = train_test_split(data, random_state=0)
model = pipeline.fit(train_data, train_data['label'])  # Use/do not use a train/test split
print("Mean accuracy: {}".format(model.score(test_data, test_data['label'])))
