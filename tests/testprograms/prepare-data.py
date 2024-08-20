""" prepare-data.py

This script prepares the data for training and evaluation.
It eliminates duplicates and warns about extremes
warns about linear regressions
It generates bootstraps and gathers the out-of-bag observations for testing
https://machinelearningmastery.com/a-gentle-introduction-to-the-bootstrap-method/

"""
from sklearn.utils import resample
import pandas as pd

'''
A useful feature of the bootstrap method is that the resulting sample of estimations often forms a Gaussian distribution. 
In additional to summarizing this distribution with a central tendency, measures of variance can be given, 
such as standard deviation and standard error. Further, a confidence interval can be calculated 
and used to bound the presented estimate. 
This is useful when presenting the estimated skill of a machine learning model.
'''
