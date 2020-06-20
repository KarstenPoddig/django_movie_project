import numpy as np
import pandas as pd

ratings = pd.read_csv('Analysen/ml-25m/ratings.csv')


# compute the percentage of full (1, 2, .., 5 stars) and half ratings (1.5, ..., 4.5)
ratings['full_rating'] = (np.mod(2*ratings['rating'], 2) == 0)


full_ratings = ratings[['userId', 'full_rating']].groupby('userId').aggregate({'full_rating': 'mean'})
