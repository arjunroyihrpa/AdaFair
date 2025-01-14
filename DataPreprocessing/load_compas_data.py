from __future__ import division
import os,sys
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn import feature_extraction
from sklearn import preprocessing
from random import seed, shuffle

# import utils as ut
import collections

SEED = 1234
seed(SEED)
np.random.seed(SEED)

"""
    The adult dataset can be obtained from: https://raw.githubusercontent.com/propublica/compas-analysis/master/compas-scores-two-years.csv
    The code will look for the data file in the present directory, if it is not found, it will download them from GitHub.
"""


def load_compas(sa):

	FEATURES_CLASSIFICATION = ["age_cat", "race", "sex", "priors_count", "c_charge_degree"] #features to be used for classification
	CONT_VARIABLES = ["priors_count"] # continuous features, will need to be handled separately from categorical features, categorical features will be encoded using one-hot
	CLASS_FEATURE = "two_year_recid" # the decision variable
	SENSITIVE_ATTRS = [sa]


	# COMPAS_INPUT_FILE = "compas-scores-two-years.csv"
	COMPAS_INPUT_FILE = "DataPreprocessing/compas-scores-two-years.csv"
	# check_data_file(COMPAS_INPUT_FILE)

	# load the data and get some stats
	df = pd.read_csv(COMPAS_INPUT_FILE)
	df = df.dropna(subset=["days_b_screening_arrest"]) # dropping missing vals
	
	# convert to np array
	data = df.to_dict('list')
	for k in data.keys():
		data[k] = np.array(data[k])


	""" Filtering the data """

	# These filters are the same as propublica (refer to https://github.com/propublica/compas-analysis)
	# If the charge date of a defendants Compas scored crime was not within 30 days from when the person was arrested, we assume that because of data quality reasons, that we do not have the right offense. 
	idx = np.logical_and(data["days_b_screening_arrest"]<=30, data["days_b_screening_arrest"]>=-30)


	# We coded the recidivist flag -- is_recid -- to be -1 if we could not find a compas case at all.
	idx = np.logical_and(idx, data["is_recid"] != -1)

	# In a similar vein, ordinary traffic offenses -- those with a c_charge_degree of 'O' -- will not result in Jail time are removed (only two of them).
	idx = np.logical_and(idx, data["c_charge_degree"] != "O") # F: felony, M: misconduct

	# We filtered the underlying data from Broward county to include only those rows representing people who had either recidivated in two years, or had at least two years outside of a correctional facility.
	idx = np.logical_and(idx, data["score_text"] != "NA")

	# we will only consider blacks and whites for this analysis
	idx = np.logical_and(idx, np.logical_or(data["race"] == "African-American", data["race"] == "Caucasian"))

	# select the examples that satisfy this criteria
	for k in data.keys():
		data[k] = data[k][idx]



	print (collections.Counter(data[sa]))

	test = pd.DataFrame.from_dict(data)
	# print test
	""" Feature normalization and one hot encoding """

	# convert class label 0 to -1
	y = data[CLASS_FEATURE]
	y[y==0] = -1

	X = np.array([]).reshape(len(y), 0) # empty array with num rows same as num examples, will hstack the features to it
	x_control = defaultdict(list)

	feature_names = []
	index = -1
	saIndex = 0
	for attr in FEATURES_CLASSIFICATION:
		index +=1

		vals = data[attr]
		if attr in CONT_VARIABLES:
			vals = [float(v) for v in vals]
			vals = preprocessing.scale(vals) # 0 mean and 1 variance  
			vals = np.reshape(vals, (len(y), -1)) # convert from 1-d arr to a 2-d arr with one col

		else: # for binary categorical variables, the label binarizer uses just one var instead of two
			lb = preprocessing.LabelBinarizer()
			lb.fit(vals)
			vals = lb.transform(vals)

		# add to sensitive features dict
		if attr in SENSITIVE_ATTRS:
			x_control[attr] = vals


		# add to learnable features
		X = np.hstack((X, vals))

		if attr in CONT_VARIABLES: # continuous feature, just append the name
			feature_names.append(attr)
		else: # categorical features
			if vals.shape[1] == 1: # binary features that passed through lib binarizer
				feature_names.append(attr)
			else:
				for k in lb.classes_: # non-binary categorical features, need to add the names for each cat
					feature_names.append(attr + "_" + str(k))


	# convert the sensitive feature to 1-d array
	x_control = dict(x_control)
	for k in x_control.keys():
		assert(x_control[k].shape[1] == 1) # make sure that the sensitive feature is binary after one hot encoding
		x_control[k] = np.array(x_control[k]).flatten()

	# sys.exit(1)

	"""permute the date randomly"""
	# perm = range(0,X.shape[0])
	# shuffle(perm)
	# X = X[perm]
	# y = y[perm]
	# for k in x_control.keys():
	# 	x_control[k] = x_control[k][perm]
	feature_names.append('target')
	print ("Features we will be using for classification are:", feature_names, "\n")

	# pd.DataFrame(np.c_[X, y]).to_csv("test_compas_X.csv", header=feature_names)
	# print np.sum(X[:,feature_names.index(SENSITIVE_ATTRS[0])])

	return X, y, feature_names.index(SENSITIVE_ATTRS[0]), 0, x_control

