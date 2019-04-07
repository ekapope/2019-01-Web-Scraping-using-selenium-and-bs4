# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 19:47:53 2019

@author: Chris
"""

import os
os.chdir(r"C:\Users\eviriyakovithya\Documents\GitHub\2019-01-Web-Scraping-using-selenium-and-bs4")

# import data manipulation library
import numpy as np
import pandas as pd

# import data visualization library
import matplotlib.pyplot as plt
import seaborn as sns

# import scientific computing library
import scipy

# import sklearn data preprocessing
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import make_pipeline,Pipeline
from sklearn.pipeline import Pipeline

# import sklearn model class
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor

# import sklearn model selection
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score, cross_val_predict, validation_curve
# import sklearn model evaluation regression metrics
from sklearn import metrics
from sklearn.metrics import make_scorer,mean_squared_error, r2_score

###############################################################################
df=pd.read_csv(r"data\regression_data\df_cleaned_for_ML_regression.csv")
#goal is to predict current price, drop all duplicates
print(df.info())
print(df['district'].nunique())
print(df['tran_type1'].nunique())

# exclude everything with a price above or below 3 standard deviations (i.e. outliers)
df = df[np.abs(df["price_sqm"]-df["price_sqm"].mean())<=(3*df["price_sqm"].std())]

#get dummies for district column
#df = pd.get_dummies(df, columns=['district'])
df = pd.get_dummies(df, columns=['district'])
#drop id, name columns
df = df.drop(['id', 'name','bld_age',
              'tran_type1','tran_type2','tran_type3', 'tran_type4', 'tran_type5',
              'tran_name1','tran_name2', 'tran_name3', 'tran_name4', 'tran_name5'], axis=1)
#df = df.drop(['id', 'name'], axis=1)

print(df.info())
df['price_sqm'].describe()
plt.hist(df['price_sqm'])

corr_matrix = df.corr()
np.abs(corr_matrix["price_sqm"]).sort_values(ascending=False)

# select all features to evaluate the feature importances
X = df.drop('price_sqm', axis=1)
y = df['price_sqm']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=121)

###############################################################################
# define function for output and plotting
def rmse_cv(model,n_folds=5):
    kf = KFold(n_folds, shuffle=True, random_state=121)
    rmse= np.sqrt(-cross_val_score(model, X_train, y_train, scoring="neg_mean_squared_error", cv = kf))
#    cv_scores = cross_val_score(model, X, y, cv=kf)
    model.fit(X_train, y_train) 
    y_pred = model.predict(X_test)
    r_sq_score = r2_score(y_test, y_pred)
    plt.scatter(y_test, y_pred)    
    plt.title(model)
    plt.xlabel("True prices")
    plt.ylabel("Predicted prices")  
#    plt.text(-1,220000, ' R-squared = {}'.format(float(cv_scores.mean())))
#    plt.text(-1,200000, ' R-squared Std = {}'.format(float(cv_scores.std())))
#    plt.text(-1,180000, ' MSE = {}'.format(round(float(mean_squared_error(y_test, predicted)), 2)))
    plt.show()
    return(rmse, r_sq_score)
###############################################################################
#ols = make_pipeline(RobustScaler(), LinearRegression())
#rmse,r_sq_score = rmse_cv(ols)
#print('RMS: {:.2f}'.format(rmse.mean()),'r2_score: '+ str(r_sq_score))
###############################################################################
# ridge regression
# manually tune alpha(s)
alpha_list =[0.0001,0.001,0.01,0.1,1,10,100]
result=[]
for alpha_val in alpha_list:
    ridge = make_pipeline(RobustScaler(), Ridge(alpha= alpha_val))
    rmse,r_sq_score = rmse_cv(ridge)
    print('RMS: {:.2f}'.format(rmse.mean()),'r2_score: '+ str(r_sq_score))
    result.append([alpha_val,np.mean(rmse),r_sq_score])
ridge_result = pd.DataFrame(result, columns = ['alpha_val','np.mean(rmse)','r_sq_score'])
###############################################################################
from sklearn.model_selection import GridSearchCV
# Create the parameter grid based on the results of random search 
param_grid = {
    'bootstrap': [True],
    'max_depth': [80, 90, 100, 110],
    'max_features': [9, 40],
    'min_samples_leaf': [3, 4, 5],
    'min_samples_split': [8, 10, 12],
    'n_estimators': [100, 200, 300, 1000]
}
# Create a based model
rf = RandomForestRegressor()
# Instantiate the grid search model
grid_search = GridSearchCV(estimator = rf, param_grid = param_grid, 
                          cv = 5, n_jobs = -1, verbose = 2)
#Fitting 5 folds for each of 288 candidates, totalling 1440 fits
#[Parallel(n_jobs=-1)]: Using backend LokyBackend with 4 concurrent workers.
#[Parallel(n_jobs=-1)]: Done  33 tasks      | elapsed:   12.4s
#[Parallel(n_jobs=-1)]: Done 154 tasks      | elapsed:   44.9s
#[Parallel(n_jobs=-1)]: Done 357 tasks      | elapsed:  2.5min
#[Parallel(n_jobs=-1)]: Done 640 tasks      | elapsed:  4.2min
#[Parallel(n_jobs=-1)]: Done 1005 tasks      | elapsed:  7.2min
#[Parallel(n_jobs=-1)]: Done 1440 out of 1440 | elapsed: 11.4min finished
# Fit the grid search to the data
grid_search.fit(X_train, y_train)
grid_search.best_params_
#{'bootstrap': True,
# 'max_depth': 80,
# 'max_features': 40,
# 'min_samples_leaf': 3,
# 'min_samples_split': 8,
# 'n_estimators': 200}
best_grid = grid_search.best_estimator_
rf_best = make_pipeline(RobustScaler(), best_grid)
rmse,r_sq_score = rmse_cv(rf)
print('RMS: {:.2f}'.format(rmse.mean()),'r2_score: '+ str(r_sq_score))
###############################################################################
param_grid = {
    'learning_rate': [0.05],
    'max_depth': [10, 20, 50, 100],
    'max_features': ['sqrt'],
    'min_samples_leaf': [3, 5, 10],
    'min_samples_split': [5, 10, 15],
    'n_estimators': [100, 200, 300, 1000,3000],    
    'loss': ['huber'],
    'random_state': [121]   
}
# Create a based model
GBoost = GradientBoostingRegressor()
# Instantiate the grid search model
grid_search_GBoost = GridSearchCV(estimator = GBoost, param_grid = param_grid, 
                          cv = 5, n_jobs = -1, verbose = 2)

grid_search_GBoost.fit(X_train, y_train)
grid_search_GBoost.best_params_
#Fitting 5 folds for each of 180 candidates, totalling 900 fits
#[Parallel(n_jobs=-1)]: Using backend LokyBackend with 4 concurrent workers.
#[Parallel(n_jobs=-1)]: Done  33 tasks      | elapsed:  2.0min
#[Parallel(n_jobs=-1)]: Done 154 tasks      | elapsed:  8.4min
#[Parallel(n_jobs=-1)]: Done 357 tasks      | elapsed: 22.7min
#[Parallel(n_jobs=-1)]: Done 640 tasks      | elapsed: 43.2min
#[Parallel(n_jobs=-1)]: Done 900 out of 900 | elapsed: 62.8min finished
#{'learning_rate': 0.05,
# 'loss': 'huber',
# 'max_depth': 50,
# 'max_features': 'sqrt',
# 'min_samples_leaf': 10,
# 'min_samples_split': 5,
# 'n_estimators': 3000,
# 'random_state': 121}
best_grid_search_GBoost = grid_search_GBoost.best_estimator_
GBoost_best = make_pipeline(RobustScaler(), best_grid_search_GBoost)
rmse,r_sq_score = rmse_cv(GBoost_best)
print('RMS: {:.2f}'.format(rmse.mean()),'r2_score: '+ str(r_sq_score))

#GBoost = GradientBoostingRegressor(n_estimators=3000, learning_rate=0.05,
#                                   max_depth=4, max_features='sqrt',
#                                   min_samples_leaf=15, min_samples_split=10, 
#                                   loss='huber', random_state =121)
#rmse,r_sq_score = rmse_cv(GBoost)
#print('RMS: {:.2f}'.format(rmse.mean()),'r2_score: '+ str(r_sq_score))