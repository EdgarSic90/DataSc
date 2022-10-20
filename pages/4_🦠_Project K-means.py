#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:51:58 2022

@author: edgarsicat
"""

import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('K-means Clustering')

sns.set_theme()
# -----------------------------------------------------------

# Helper functions
# -----------------------------------------------------------
# Load data from external source
@st.cache
def load_data():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/ThuwarakeshM/PracticalML-KMeans-Election/master/voters_demo_sample.csv"
    )
    return df


df = load_data()


def run_kmeans(df, n_clusters=2):
    kmeans = KMeans(n_clusters, random_state=0).fit(df[["Age", "Income"]])

    fig, ax = plt.subplots(figsize=(16, 9))

    ax.grid(False)
    ax.set_facecolor("#FFF")
    ax.spines[["left", "bottom"]].set_visible(True)
    ax.spines[["left", "bottom"]].set_color("#4a4a4a")
    ax.tick_params(labelcolor="#4a4a4a")
    ax.yaxis.label.set(color="#4a4a4a", fontsize=20)
    ax.xaxis.label.set(color="#4a4a4a", fontsize=20)
    # --------------------------------------------------

    # Create scatterplot
    ax = sns.scatterplot(
        ax=ax,
        x=df.Age,
        y=df.Income,
        hue=kmeans.labels_,
        palette=sns.color_palette("colorblind", n_colors=n_clusters),
        legend=None,
    )

    # Annotate cluster centroids
    for ix, [age, income] in enumerate(kmeans.cluster_centers_):
        ax.scatter(age, income, s=200, c="#a8323e")
        ax.annotate(
            f"Cluster #{ix+1}",
            (age, income),
            fontsize=25,
            color="#a8323e",
            xytext=(age + 5, income + 3),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#a8323e", lw=2),
            ha="center",
            va="center",
        )

    return fig



container = st.container()

#container.write("Select your perfect number of clusters !")
n_clusters = container.slider("Select your perfect number of clusters !",min_value=2,max_value=15,)
   
# You can call any Streamlit command, including custom components:
container.write(run_kmeans(df, n_clusters=n_clusters))

df_display = container.checkbox("Display Raw Data", value=False)
if df_display:
    container.write(df)
    
    
#container.write("This is outside the container")






