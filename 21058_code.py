# -*- coding: utf-8 -*-
"""21058_code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iMxXHwDZBHNNiLi2WBisYxf4Z6mygY7h
"""

import csv,os,re,sys,codecs
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib,  statistics
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_selection import SelectKBest,chi2
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from collections import Counter
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

data=pd.read_csv('dataset.csv')
data

data.isnull().sum()

data.dtypes

y=data['URL'].unique()
y.size

y=data['CHARSET'].unique()
y.size

y=data['SERVER'].unique()
y.size

y=data['WHOIS_COUNTRY'].unique()
y.size

y=data['WHOIS_STATEPRO'].unique()
y.size

y=data['WHOIS_REGDATE'].unique()
y.size

y=data['WHOIS_UPDATED_DATE'].unique()
y.size

# Create a list of column names containing string values
string_columns = [col for col in data.columns if data[col].dtype == 'object']

if string_columns:
    print("Columns containing string values:", string_columns)
else:
    print("No column contains string values.")

dum=data.copy()
pre_dum=dum.drop(columns=['URL', 'CHARSET', 'SERVER', 'WHOIS_COUNTRY',
                          'WHOIS_STATEPRO', 'WHOIS_REGDATE', 'WHOIS_UPDATED_DATE'],axis=1)
pre = pre_dum.interpolate()
corrmat = pre.corr()
f, ax = plt.subplots(figsize=(25,19))
sns.heatmap(corrmat, square=True, annot = True, annot_kws={'size':10})
plt.savefig("output1.png")

one_hot_encoded_data = pd.get_dummies(data, columns = ['URL', 'CHARSET', 'SERVER', 'WHOIS_COUNTRY', 'WHOIS_STATEPRO', 'WHOIS_REGDATE', 'WHOIS_UPDATED_DATE'])
print(one_hot_encoded_data)

df = one_hot_encoded_data.interpolate()
print(df.isnull().sum())

y_train = df['Type']
x_train = df.drop(columns = ['Type'],axis=1)
smote = SMOTE(random_state=42)
data,labels = smote.fit_resample(x_train,y_train)

plt.hist(labels)
plt.ylabel('frequency count')
plt.xlabel('data')
plt.title('labels')
plt.show()

plt.figure()
plt.title("Use of Special Characters in URL", fontsize=20)
plt.xlabel("Count Of special characters",fontsize=18)
plt.ylabel("Number Of URLs", fontsize=18)

# Assuming 'SERVER' is the column you want to use for counting
sns.countplot(x='NUMBER_SPECIAL_CHARACTERS', data=data, order=data['NUMBER_SPECIAL_CHARACTERS'].value_counts().index)

plt.ylim(0, 400)  # Adjust the y-axis limit as needed
plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
plt.show()

plt.savefig("output3.png")

plt.figure()
plt.title("Length of URL", fontsize=20)
plt.xlabel("Count of url length", fontsize=18)
plt.ylabel("Number Of URLs", fontsize=18)

# Assuming 'SERVER' is the column you want to use for counting
sns.countplot(x='URL_LENGTH', data=data, order=data['URL_LENGTH'].value_counts().index)

plt.ylim(0, 100)  # Adjust the y-axis limit as needed
#plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
plt.show()
plt.savefig("output4.png")

missing_vals = (df.isnull().sum())
print(missing_vals[missing_vals == 0])

print('\n\t### Training Decision Tree Classifier ### \n')
clf = DecisionTreeClassifier(random_state=40)
clf_parameters = {
            'clf__criterion':('gini', 'entropy'),
            'clf__max_features':('auto', 'sqrt', 'log2'),
            'clf__max_depth':(10,40,45,60),
            'clf__ccp_alpha':(0.009,0.01,0.05,0.1),
            }

skf = StratifiedKFold(n_splits=5)
#skf.get_n_splits(data,labels)
predicted_class_labels=[]; actual_class_labels=[];
count=0; probs=[];
for train_index, test_index in skf.split(data,labels):
  X_train=[]; y_train=[]; X_test=[]; y_test=[]
  for item in train_index:
    X_train.append(data[item])
    y_train.append(labels[item])
  for item in test_index:
    X_test.append(data[item])
    y_test.append(labels[item])
    count+=1

pipeline = Pipeline([('feature_selection', SelectKBest(chi2, k=10)),('clf', clf)])
grid = GridSearchCV(pipeline,clf_parameters,scoring='f1_macro',cv=10)
grid.fit(X_train,y_train)
clf= grid.best_estimator_
print('\n\n The best set of parameters of the pipiline are: ')
print(clf)

class_names=list(Counter(labels).keys())
class_names = [str(x) for x in class_names]
# print('\n\n The classes are: ')
# print(class_names)

print('\n ##### Classification Report on Training Data ##### \n')
print(classification_report(actual_class_labels, predicted_class_labels, target_names=class_names))

pr=precision_score(actual_class_labels, predicted_class_labels, average='macro')
print ('\n Precision:\t'+str(pr))

rl=recall_score(actual_class_labels, predicted_class_labels, average='macro')
print ('\n Recall:\t'+str(rl))

fm=f1_score(actual_class_labels, predicted_class_labels, average='macro')
print ('\n F1-Score:\t'+str(fm))

disp = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=['Non-mallicious','Mallicious'])
disp.plot()
plt.show()
plt.savefig("out1.png")

print('***Training Logistic Regression Classifier***')
clf = LogisticRegression(solver='liblinear',class_weight='balanced')
clf_parameters = {
            'clf__random_state':(0,10),
            'clf__solver':('liblinear','lbfgs','newton-cg')
            }

pipeline = Pipeline([('feature_selection', SelectKBest(chi2, k=10)),('clf', clf),])
grid = GridSearchCV(pipeline,clf_parameters,scoring='f1_macro',cv=5)
grid.fit(training_data,training_cat)
clf= grid.best_estimator_
print('\n\n The best set of parameters of the pipiline are: ')
print(clf)
predicted=clf.predict(validation_data)

# Evaluation
print('\n *************** Confusion Matrix ***************  \n')
matrix=confusion_matrix(validation_cat, predicted)
print(matrix)

class_names=list(Counter(validation_cat).keys())
class_names = [str(x) for x in list(Counter(validation_cat).keys())]

# Classification report
print('\n ##### Classification Report ##### \n')
print(classification_report(validation_cat, predicted, target_names=class_names))

pr=precision_score(validation_cat, predicted, average='macro')
print ('\n Precision:\t'+str(pr))

rl=recall_score(validation_cat, predicted, average='macro')
print ('\n Recall:\t'+str(rl))

fm=f1_score(validation_cat, predicted, average='macro')
print ('\n F1-Score:\t'+str(fm))

disp = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=['Non-mallicious','Mallicious'])
disp.plot()
plt.show()
plt.savefig("out2.png")

print('***Training Linear SVC Classifier***')
clf = svm.LinearSVC(class_weight='balanced')
clf_parameters = {
            'clf__C':(0.1,1,100),
            }

pipeline = Pipeline([('feature_selection', SelectKBest(chi2, k=10)),('clf', clf),])

grid = GridSearchCV(pipeline,clf_parameters,scoring='f1_macro',cv=5)
grid.fit(training_data,training_cat)
clf= grid.best_estimator_
print('\n\n The best set of parameters of the pipiline are: ')
print(clf)
predicted=clf.predict(validation_data)

# Evaluation
print('\n *************** Confusion Matrix ***************  \n')
matrix=confusion_matrix(validation_cat, predicted)
print(matrix)

class_names=list(Counter(validation_cat).keys())
class_names = [str(x) for x in list(Counter(validation_cat).keys())]

# Classification report
print('\n ##### Classification Report ##### \n')
print(classification_report(validation_cat, predicted, target_names=class_names))

pr=precision_score(validation_cat, predicted, average='macro')
print ('\n Precision:\t'+str(pr))

rl=recall_score(validation_cat, predicted, average='macro')
print ('\n Recall:\t'+str(rl))

fm=f1_score(validation_cat, predicted, average='macro')
print ('\n F1-Score:\t'+str(fm))

disp = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=['Non-mallicious','Mallicious'])
disp.plot()
plt.show()
plt.savefig("out3.png")

print('\n\t### Training Multinomial Naive Bayes Classifier ### \n')
clf = MultinomialNB(fit_prior=True, class_prior=None)
clf_parameters = {
            'clf__alpha':(0,1),
            }
pipeline = Pipeline([('feature_selection', SelectKBest(chi2, k=10)),('clf', clf),])

grid = GridSearchCV(pipeline,clf_parameters,scoring='f1_macro',cv=5)
grid.fit(training_data,training_cat)
clf= grid.best_estimator_
print('\n\n The best set of parameters of the pipiline are: ')
print(clf)
predicted=clf.predict(validation_data)

# Evaluation
print('\n *************** Confusion Matrix ***************  \n')
matrix=confusion_matrix(validation_cat, predicted)
print(matrix)

class_names=list(Counter(validation_cat).keys())
class_names = [str(x) for x in list(Counter(validation_cat).keys())]

        # Classification report
print('\n ##### Classification Report ##### \n')
print(classification_report(validation_cat, predicted, target_names=class_names))

pr=precision_score(validation_cat, predicted, average='macro')
print ('\n Precision:\t'+str(pr))

rl=recall_score(validation_cat, predicted, average='macro')
print ('\n Recall:\t'+str(rl))

fm=f1_score(validation_cat, predicted, average='macro')
print ('\n F1-Score:\t'+str(fm))

disp = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=['Non-mallicious','Mallicious'])
disp.plot()
plt.show()
plt.savefig("out4.png")

print('\n\t ### Training Random Forest Classifier ### \n')
clf = RandomForestClassifier(max_features=None,class_weight='balanced')
clf_parameters = {
            'clf__criterion':('entropy','gini'),
            'clf__n_estimators':(30,50,100),
            'clf__max_depth':(10,20,30,50,100,200),
            }
pipeline = Pipeline([('feature_selection', SelectKBest(chi2, k=10)),('clf', clf)])

grid = GridSearchCV(pipeline,clf_parameters,scoring='f1_macro',cv=5)
grid.fit(training_data,training_cat)
clf= grid.best_estimator_
print('\n\n The best set of parameters of the pipiline are: ')
print(clf)
predicted=clf.predict(validation_data)

# Evaluation
print('\n *************** Confusion Matrix ***************  \n')
matrix=confusion_matrix(validation_cat, predicted)
print(matrix)

class_names=list(Counter(validation_cat).keys())
class_names = [str(x) for x in list(Counter(validation_cat).keys())]

# Classification report
print('\n ##### Classification Report ##### \n')
print(classification_report(validation_cat, predicted, target_names=class_names))

pr=precision_score(validation_cat, predicted, average='macro')
print ('\n Precision:\t'+str(pr))

rl=recall_score(validation_cat, predicted, average='macro')
print ('\n Recall:\t'+str(rl))

fm=f1_score(validation_cat, predicted, average='macro')
print ('\n F1-Score:\t'+str(fm))

disp = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=['Non-mallicious','Mallicious'])
disp.plot()
plt.show()
plt.savefig("out5.png")











































