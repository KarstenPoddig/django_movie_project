from sklearn.metrics import precision_score, \
    f1_score, recall_score, mean_squared_error, mean_absolute_error
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from movie_app.recommendation_models.load_data import load_movie_index,\
    load_similarity_matrix

similarity_matrix = load_similarity_matrix()
movie_index = load_movie_index().set_index('movieId')


# create test set

ratings = pd.read_csv('Analysen/ml-25m/ratings.csv')
ratings_per_user = ratings.groupby('userId')[['movieId']].count()
ratings_per_user.reset_index(inplace=True)
relevant_user = ratings_per_user.sample(2000).userId

ratings = ratings[ratings.userId.isin(relevant_user)]
ratings = ratings[ratings.movieId.isin(movie_index.index)]

ratings_train = ratings[:0]
ratings_test = ratings[:0]

for user in relevant_user:
    ratings_user = ratings[ratings.userId == user]
    ratings_user_train, ratings_user_test = train_test_split(ratings_user,
                                                             test_size=0.05)
    print('user: ' + str(user) +
          ', train_size: ' + str(ratings_user_train.shape) +
          ', test_size: ' + str(ratings_user_test.shape))
    ratings_train = ratings_train.append(ratings_user_train)
    ratings_test = ratings_test.append(ratings_user_test)


ratings_test['predicted_rating'] = 0
ratings_test['sum_similarity'] = 0

for user in relevant_user:
    ratings_test_user = ratings_test[ratings_test.userId == user]
    ratings_train_user = ratings_train[ratings_train.userId == user]
    similarity_matrix_user = similarity_matrix[movie_index.loc[ratings_test_user.movieId].to_numpy().reshape(-1), :]
    similarity_matrix_user = similarity_matrix_user[:, movie_index.loc[ratings_train_user.movieId].to_numpy().reshape(-1)]
    ratings_train_array = ratings_train_user.rating.to_numpy()
    nr_relev_movies = min(10, similarity_matrix_user.shape[1])
    for i in range(similarity_matrix_user.shape[0]):
        row = similarity_matrix_user[i]
        similarity_matrix_user[i, row.argsort()[:-nr_relev_movies]] = 0
    sum_similarity_array = np.sum(similarity_matrix_user, 1)
    ratings_test_user['predicted_rating'] = np.dot(similarity_matrix_user, ratings_train_array)
    ratings_test_user['sum_similarity'] = sum_similarity_array
    ratings_test.loc[ratings_test_user.index, 'predicted_rating'] = ratings_test_user['predicted_rating']
    ratings_test.loc[ratings_test_user.index, 'sum_similarity'] = ratings_test_user['sum_similarity']


ratings_test['predicted_rating'] = ratings_test['predicted_rating']/ratings_test['sum_similarity']
ratings_test['error'] = ratings_test['rating'] - ratings_test['predicted_rating']
ratings_test['predicted_rating'] = np.round(ratings_test['predicted_rating']/0.5)*0.5
print(mean_squared_error(ratings_test['rating'], ratings_test['predicted_rating']))
print(mean_absolute_error(ratings_test['rating'], ratings_test['predicted_rating']))
print(np.corrcoef(ratings_test['error'], ratings_test['sum_similarity']))


import matplotlib.pyplot as plt

plt.hist(ratings_test['rating'], bins=50)
plt.hist(ratings_test['predicted_rating'], bins=50)
plt.show()
