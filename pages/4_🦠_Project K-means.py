#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:51:58 2022

@author: edgarsicat
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import random
from scipy.spatial.distance import cdist

st.title('K-means Clustering from scratch')

st.write("""
         Developping a K-means clustering model without the very famous sklearn package was one of my first academic project.
         It's a great way to translate basic mathematical principles into python code !
         """)
st.write("You'll find the code on this [Jupyter notebook](https://github.com/EdgarSic90/DataSc/blob/master/K-MEANS%20FROM%20SCRATCH/K-means%20Final%20Edgar%20SICAT.ipynb) & some analysis of the algorithm")
st.write("Below you'll be able to test the model with your number of clusters on a customer data set")

sns.set_theme()
# -----------------------------------------------------------

# Helper functions
# -----------------------------------------------------------
# Load data from external source
@st.cache
def load_data():
    Customer_data = pd.read_csv('Customers_practice.csv')
    return Customer_data


df = load_data()


@st.cache
def euclidian_distance(v1,v2):
    return np.sqrt(np.sum((v1-v2)**2))

@st.cache
class Kmeans:
    

    def __init__(self, k, X):     # Storing value inside the class so we can reuse them in the functions
        self.k = k  
        self.nb_it = 100         # 100 iteration max
        self.nb_samples, self.nb_features = X.shape
        self.X = X
        self.X_array = np.array(X)
    
  
    def init_centroids(self, X):    
        Centroids = random.sample(list(X), self.k)          # Initialisation by choosing k random centroid from X (data set)
        return np.array(Centroids)
        
     
    def cluster_calc(self, X, Centroids):
        clusters = [ [] for i in range(self.k)]          # Creation of k number of Clusters. First we create k empty array inside a list 
        for i,X in enumerate(X):                         # Now for each of these cluster we will put indexes of X
            closest_centroid = np.argmin([[euclidian_distance(X,cent)] for j, cent in enumerate(Centroids)])  # comprehension list calculating the dist between each centroid and X point. and then getting the index of the smallest one
            clusters[closest_centroid].append(i)                              # appending the index i of X inside the corresponding class cluster
        return np.array(clusters)
    

    def create_new_centroid(self, clusters, X):          
        Centroids = np.zeros((self.k, self.nb_features))           # populating new centroids with 0
        for i, clust in enumerate(clusters):                       
            new_centroid = np.mean(X[clust], axis=0)              # getting the mean of each X from the clusters
            Centroids[i] = new_centroid
        return Centroids
    

    def predict(self, X, plot = True):                      # argument plot is used to activate or not the plot function inside
        Centroids_init = self.init_centroids(X)              # creating the first centroids
        res = "Initialisation" + '\n'  
        count = 0                                            # creating a count value that will help us control the while loop
        centroid_list = []                                   # centroid list that will be use to compare centroids for convergence or not
        _class = np.zeros((self.nb_samples,))                # Empy array that will be populated with X classes in order to plot them
        converged = False                                    # boolen that will help us control the loop
        
        while count < self.nb_it and not converged:
            if count == 0:                                   # First step in the loop, initation, appending centroid, calculating first cluster
                centroid_list.append(Centroids_init)
                cluster = self.cluster_calc(X, Centroids_init)
                Centroids_looped = Centroids_init 
                count += 1                                   # + 1 count for the first itteration
            else:
                Centroids_looped = self.create_new_centroid(cluster, X)          # after the first step, this will loop unless 2 elments from the centroid list are not different
                cluster = self.cluster_calc(X, Centroids_looped)
                centroid_list.append(Centroids_looped)
                count += 1
                if np.array_equal((centroid_list[count-1]),(centroid_list[count-2])) == True:
                    converged = True                                              # after some iteration, 2 centroids are equals and so converged, we are passing true to the boolean
                    for i, x in enumerate(cluster):                               # creation of the class list with the final cluster
                        _class[x] = round(i)
                    if plot == True:                                              # fonction plot will be call if desired
                        self.plot_fig(X, _class, centroid_list[-1])
                else:
                    pass

            
            # print(str('Epoch: {0} | new centroids: {1} '.format(count, Centroids_looped))+ '\n')
        if plot == True:
            return self.plot_fig(X, _class, centroid_list[-1])
        else:
            return Centroids_looped, cluster

    def plot_fig(self, X, y, Centroids):                                             # plot foncction thta display in a dynamic way, Clusters with they class and centroids
        Data = pd.DataFrame(X, columns=["Annual_Income_(k$)", "Spending_Score"])
        Y = pd.DataFrame(y, columns=["Class"])
        Result = pd.concat([Data, Y], axis=1)                                        # Concatenating X data set and the class list
        Centroid = pd.DataFrame(Centroids, columns=["Annual_Income_(k$)", "Spending_Score"])
        Class = pd.DataFrame(list(range(0,len(Centroids))) , columns=["ClassCentoid"])
        Result2 = pd.concat([Centroid, Class], axis=1)                               # Concatenating the Centroid list with an array created with class
        sns.set(rc={'figure.figsize':(11.7,8.27)})
        ax = sns.scatterplot(data=Result, x="Annual_Income_(k$)", y="Spending_Score", hue="Class", palette="bright", legend=False)      # Clusters display
        ax = sns.scatterplot(data=Result2, x="Annual_Income_(k$)", y="Spending_Score", hue="ClassCentoid", palette="dark", s=100, legend=False)   # Centroid display
        return plt


container = st.container()

#container.write("Select your perfect number of clusters !")
n_clusters = container.slider("Select your perfect number of clusters !",min_value=2,max_value=13,)
   
# You can call any Streamlit command, including custom components:
clf = Kmeans(n_clusters, df)
clf_centroid = clf.init_centroids(df.values)
clf_cluster = clf.cluster_calc(df.values, clf_centroid)
container.pyplot(clf.predict(df.values, plot=True))

df_display = container.checkbox("Display Raw Data", value=True)
if df_display:
    container.write(df)
    




