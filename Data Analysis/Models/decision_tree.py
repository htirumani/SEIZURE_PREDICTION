import numpy as np
import pandas as pd
import datetime
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

from utils import custom_train_test_split

from pprint import pprint

split_prop = 0.80

X_train, y_train, X_test, y_test = custom_train_test_split(['HEART', 'STEP', 'NIGHTTIME', 'MEAN_10MIN_HR', 'SD_10MIN_HR'], [u0_path, u2_path], split_prop)

# define and fit Decision Tree model
model = DecisionTreeClassifier(criterion='entropy', max_depth=10, splitter='best', random_state=0).fit(X_train, y_train)

# print model performance
print('Training Accuracy: ', model.score(X_train, y_train))
print('Testing Accuracy: ', model.score(X_test, y_test))

y_hat = model.predict(X_test)
errs = y_hat != y_test
fn = y_test & np.logical_not(y_hat)
fp = np.logical_not(y_test) & y_hat

print()
print('Confusion Matrix\n', confusion_matrix(y_test, y_hat))

print()
print('Classification Report\n', classification_report(y_test, y_hat))

print()
print('Testing Errors: {} / {}'.format(sum(errs), y_hat.shape[0]))
print('Num False Negatives:', sum(fn))
print('Num False Positives:', sum(fp))

print()
print('False Negative Rate: ', sum(fn) / sum(y_test))
print('False Positive Rate: ', sum(fp) / sum(np.logical_not(y_test)))