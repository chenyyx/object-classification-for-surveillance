#!/usr/bin/python

import sys, os, time

from sklearn.svm import LinearSVC
from sklearn import decomposition

import numpy as np
from sklearn import datasets
from skimage.feature import hog
from sklearn.utils import shuffle
from sklearn import metrics
import sys
from numpy import genfromtxt

extnsn = "_grey_ftr.csv"
Rsol = 30

print "LinearSVC results for ", extnsn, " with feature and resolution = ", Rsol

train_dir = "CSVs/" + sys.argv[1].rstrip('/')
test_dir = "CSVs/" + sys.argv[2].rstrip('/')


X_train, y_train = [], []
X_test, y_test = [], []

X_train_o = genfromtxt(train_dir +  str(Rsol) + extnsn, delimiter=',', dtype=int)
y_train = genfromtxt(train_dir +  str(Rsol) +"_lbl.csv", delimiter=',', dtype=int)
X_test_o =  genfromtxt(test_dir +  str(Rsol) + extnsn, delimiter=',', dtype=int)
y_test =  genfromtxt(test_dir +  str(Rsol) +"_lbl.csv", delimiter=',', dtype=int)


def get_HoG(xs, size_cell=4, size_block=4, orientation=7):
    hog_xs = []
    for x in xs:
        fd = hog(x.reshape((Rsol, Rsol)),
                    orientations=orientation,
                    pixels_per_cell=(size_cell, size_cell),
                    cells_per_block=(size_block, size_block), visualise=False)
        hog_xs.append(fd)
    return hog_xs

X_train_o, X_test_o = get_HoG(X_train_o), get_HoG(X_test_o)

def get_PCA(Xs, n_components):
    pca = decomposition.PCA(n_components=n_components)
    print "PCA: n_features = ", len(Xs[0]),
    # pca.fit(Xs)
    Xs1 = pca.fit_transform(Xs)
    print "PCA: n_components = ", len(Xs1[0]),
    return Xs1

def build_data_sets(n_components=0):
    global X_train, y_train, X_test, y_test, X_train_o, X_test_o
    
    if n_components:
        X_train = get_PCA(X_train_o, n_components)
        X_test = get_PCA(X_test_o, n_components)
    else:
        X_train, X_test = X_train_o, X_test_o

def get_svc_results():
    
    global X_train, y_train, X_test, y_test

    # clf = RandomForestClassifier(n_estimators=num_estimators, n_jobs=2)
    clf = LinearSVC()

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    mean_accuracy = clf.score(X_test, y_test)
    
    print ", Mean accuracy: \t", mean_accuracy
    # print "confusion matrix: \n", metrics.confusion_matrix(y_test, y_pred), "\n"

    return mean_accuracy


import warnings
import matplotlib.pyplot as plt


if __name__ == "__main__":
    start_time = time.time()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=DeprecationWarning)
        
        rang = range(0, 901, 100)
        ans = []
        for i in rang:

            build_data_sets(n_components=i)

            nTrain, nTest = len(y_train), len(y_test)
            
            if i==rang[0]:
                print "size of training-set, test-set = ", nTrain, ", ", nTest
                print "Dimension of feature vectors = ", len(X_train[0])        
            ans.append(get_svc_results())
            print "------------------------------------------------------"
        print ans
        param = "PCA-num-components"


        plt.plot(rang, ans, linewidth=2.0)
        plt.xlabel(param)
        plt.ylabel("mean accuracy")
        figdir = 'SVC_figs'
        if not os.path.exists(figdir):
            os.mkdir(figdir)
        plt.title("LinearSVC, "+extnsn+", resolution="+str(Rsol))
        plt.savefig(figdir+"/" +param +".png")
        plt.close()

    print "\n~~~~~~~~~~~~~~~~~~ total time taken = %s seconds ~~~~~~~~~~~~~~~~~~\n" %(time.time() - start_time)
