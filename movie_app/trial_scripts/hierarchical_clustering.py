from movie_app.recommendation_models.load_data import load_distance_matrix, load_movie_index
from django.contrib.auth.models import User
from movie_app.models import Rating
import pandas as pd

distance_matrix = load_distance_matrix()
movie_index = load_movie_index()

user = User.objects.filter(username='kpoddig')[0]
rated_movies = pd.DataFrame.from_records(Rating.objects.filter(user=user).values('movie_id', 'movie__title', 'movie__nrRatings', 'rating'))
# rated movies with row_indices (in matrix above)
rated_movies = pd.merge(rated_movies, movie_index, how='inner', left_on='movie_id', right_on='movieId')

distance_matrix = distance_matrix[rated_movies.row_index, :]
distance_matrix = distance_matrix[:, rated_movies.row_index]

from sklearn.cluster import AgglomerativeClustering

model = AgglomerativeClustering(n_clusters=8, affinity='precomputed', linkage='complete')
model.fit(distance_matrix)
rated_movies['cluster'] = model.labels_

rated_movies.groupby('cluster').count()

rated_movies[rated_movies.cluster == 6]