
import numpy as np
import pandas as pd


def load_similarity_matrix():
    return np.load('movie_app/recommendation_models/similarity_matrix.npy')


def load_movie_index():
    return pd.read_csv('movie_app/recommendation_models/movie_index.csv')
