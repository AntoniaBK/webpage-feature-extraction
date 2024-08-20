"""
https://www.kaggle.com/code/scratchpad/notebook371ce89873/edit
"""
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
# import scikitplot as skplt # ImportError: cannot import name 'interp' from 'scipy'
# import matplotlib as mplt

dataset = pd.read_csv('data.csv')
y = dataset.parking
features = dataset.columns
# adapt features
X = dataset[features]
print(X.head())


'''
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

model = DecisionTreeRegressor()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_mae = mean_absolute_error(y_test, y_pred)
# finding the best max leaf nodes
model = DecisionTreeRegressor(max_leaf_nodes=5, max_depth=5, random_state=1)  # ??
# give some statistics and charts about the model efficiency
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_mae = mean_absolute_error(y_test, y_pred)
# where would be the place for a N-fold cross here?

model.score(X_test, y_test)

fig = skplt.figure(figsize=(15,6))
# ! skplt is not maintained since 2018

# https://coderzcolumn.com/tutorials/machine-learning/scikit-plot-visualizing-machine-learning-algorithm-results-and-performance

ax1 = fig.add_subplot(121)
skplt.estimators.plot_feature_importances(model, feature_names=features,
                                         title="Random Forest Regressor Feature Importance",
                                         x_tick_rotation=90, order="ascending",
                                         ax=ax1)

rf_probas = model.predict_proba(X_test)
# add other models
# also:
# TUM parking page detection
# circl typosquatter parking parking page detection

proba_list = [rf_probas]  # add others
clf_names = ['Random Forest Regressor']
skplt.metrics.plot_calibration_curve(y_test, proba_list, class_names=clf_names,
                                     n_bins=15, figsize=(15,6))
skplt.metrics.confusion_matrix(y_test, y_pred,
                                    title="Confusion Matrix",
                                    cmap="Oranges",
                                    ax=ax1)
# if good
# model.fit(X, y)

'''

