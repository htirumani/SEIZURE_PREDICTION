import numpy as np
import pandas as pd
import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, classification_report, make_scorer, precision_score, recall_score, accuracy_score

from utils import custom_train_test_split
import os

from pprint import pprint

features = ['HEART', 'STEP', 'ACTIVITY', '10MIN_STEP_SUM', 'MINFROMMIDNIGHT']

# get train and test sets
split_prop = 0.80
data_path = 'Data Analysis/Dataset/final/'
fps = os.listdir(data_path)
fps.remove('combined')
fps.remove('validation')

paths = [data_path + f for f in fps]
X_train, y_train, X_test, y_test = custom_train_test_split(features, paths, split_prop)

criterion = ['gini', 'entropy']
max_depth = [2, 4, 6, 8, 10, 12]
n_estimators = [25, 50, 100]
params = {'criterion': criterion, 'max_depth': max_depth, 'n_estimators': n_estimators}
scoring = {'accuracy': make_scorer(accuracy_score), 'precision': make_scorer(precision_score), 'recall': make_scorer(recall_score)}

grid = GridSearchCV(RandomForestClassifier(), params, scoring=scoring, refit=False).fit(X_train, y_train)

results = pd.DataFrame(grid.cv_results_)
results.to_csv('random_forest_grid_results.csv')
