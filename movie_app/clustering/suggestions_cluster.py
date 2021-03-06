import random
import pandas as pd
import numpy as np
from django.db.models import Sum
from movie_app.models import Rating, Movie, ClusteringStatus, Cluster, GenomeScore
from movie_app.recommendation_models.load_data import load_distance_matrix, load_movie_index
from sklearn.cluster import AgglomerativeClustering, DBSCAN


def join_movies_to_row_index(movies):
    movie_index = load_movie_index()
    movies = movies.merge(movie_index, how='inner', left_on='movie_id',
                          right_on='movieId')
    movies.set_index('movieId', inplace=True)
    return movies


def get_rated_movies_user(user):
    rated_movies = pd.DataFrame.from_records(
        Rating.objects.filter(user=user).values()
    )
    rated_movies.set_index('movie_id', inplace=True)
    return rated_movies


def update_movie_clusters(user, movieId, rating_action):
    """This function is used to update the clusters of movies of a user.
    For every 20th movie the clustering is performed once again. Also if a rating is
    dropped, i.e. the nr of rated movies changes from 121 to 120.
    """
    nr_movies = Rating.objects.filter(user=user).count()
    if (nr_movies % 20) == 0 and nr_movies > 0:
        print('Clusters are computed')
        clustering_status = ClusteringStatus.objects.filter(user=user)[0]
        clustering_status.status = 'Pending'
        clustering_status.save()
        print('Set clustering status to pending.')

        compute_new_clusters_movies(user)

        clustering_status.status = 'Done'
        clustering_status.save()
        print('Set clustering status to done.')
    else:
        if rating_action == 'created':
            assign_movie_to_cluster(user, movieId)


def compute_new_clusters_movies(user):
    clustered_movies = get_clustered_movies_hierarchical(user)
    # delete old Clusters of user
    Cluster.objects.filter(user=user).delete()
    # saving the results
    clusters = clustered_movies.cluster.unique()
    print(clusters)
    # save clusters in Rating
    print(clustered_movies.head())
    for cluster in clusters:
        clustered_movies_cluster = clustered_movies[clustered_movies.cluster == cluster]
        cluster_description = compute_cluster_description(clustered_movies_cluster.index)
        cluster_entry = Cluster(user=user,
                                description=cluster_description)
        cluster_entry.save()
        for movieId in clustered_movies_cluster.index:
            rating = Rating.objects.filter(user=user,
                                           movie__movieId=movieId)[0]
            rating.cluster = cluster_entry
            rating.save()


def compute_cluster_description(movieIds):
    print(movieIds)
    tags_and_scores = pd.DataFrame(
        GenomeScore.objects.filter(movie_id__in=movieIds).values('tag__tag'). \
            annotate(relevance=Sum('relevance')).order_by('-relevance')[:5]
    )
    result = ', '.join(tags_and_scores['tag__tag'])
    return result


"""########################################################################

Clustering Algorithms

########################################################################"""


def get_clustered_movies(user):
    distance_rank_log = load_distance_matrix()
    rated_movies = get_rated_movies_user(user)
    rated_movies = join_movies_to_row_index(movies=rated_movies)
    distance_rank_log = distance_rank_log[rated_movies.row_index, :]
    print(distance_rank_log.shape)
    distance_rank_log = distance_rank_log[:, rated_movies.row_index]
    rated_movies['row_index'] = list(range(0, rated_movies.shape[0]))
    clustered_movies = initiate_clusters(movies=rated_movies,
                                         distance_matrix=distance_rank_log)
    print('Preclustering of movies done.')
    clustered_movies = cluster_algorithm_1(movies=clustered_movies,
                                           distance_matrix=distance_rank_log)
    return clustered_movies


def get_clustered_movies_hierarchical(user):
    distance_matrix = load_distance_matrix()
    rated_movies = get_rated_movies_user(user)
    rated_movies = join_movies_to_row_index(movies=rated_movies)
    distance_matrix = distance_matrix[rated_movies.row_index, :]
    distance_matrix = distance_matrix[:, rated_movies.row_index]
    nr_clusters = get_nr_of_clusters(nr_all_movies=rated_movies.shape[0])
    clustering_model = AgglomerativeClustering(n_clusters=nr_clusters,
                                               affinity='precomputed',
                                               linkage='complete')
    # clustering_model = DBSCAN(eps=5.0, metric='precomputed',
    #                           min_samples=5)
    clustering_model.fit(distance_matrix)
    rated_movies['cluster'] = clustering_model.labels_
    return rated_movies


def assign_movie_to_cluster(user, movieId):
    rated_movies = get_rated_movies_user(user)
    cluster_id = get_best_cluster_for_movie(movies=rated_movies,
                                            movieId=movieId)
    if cluster_id is None:
        return None
    cluster = Cluster.objects.get(id=cluster_id)
    # store cluster for movie
    movie = Movie.objects.get(movieId=movieId)
    rating_entry = Rating.objects.filter(user=user,
                                         movie=movie)[0]
    rating_entry.cluster = cluster
    rating_entry.save()
    print('Movie ' + movie.title + ' assigned to cluster ' + str(cluster) + '.')
    return None


def get_best_cluster_for_movie(movies, movieId):
    # if there are no rated movies or the aren't clustered return None
    if movies.empty or movies.cluster_id.unique()[0] is None:
        return None
    movies = join_movies_to_row_index(movies)
    distance_matrix = load_distance_matrix()
    movies['rank_log'] = distance_matrix[movies.row_index.astype('int'),
                                         int(movies.loc[movieId].row_index)]
    # return cluster where the sum of distances is minimal
    return movies.groupby('cluster_id')[['rank_log']].mean().sort_values(by='rank_log').index[0]


def get_nr_movies_per_cluster(nr_all_movies):
    nr_clusters = min(2+0.05*nr_all_movies, 8)
    nr_movies_per_cluster = int(np.ceil(nr_all_movies/nr_clusters))
    return nr_movies_per_cluster


def get_nr_of_clusters(nr_all_movies):
    nr_clusters = round(min(2+0.03*nr_all_movies, 5))
    return nr_clusters


def get_rank_score(movies, distance_matrix):
    distance_subset = distance_matrix[movies.row_index, :]
    distance_subset = distance_subset[:, movies.row_index]
    score = sum(sum(distance_subset))
    return score


def initiate_clusters(movies, distance_matrix):
    """This function computes a first clustering of the movies with the
    distance matrix."""
    nr_movies_per_cluster = get_nr_movies_per_cluster(nr_all_movies=movies.shape[0])
    movies['cluster'] = 0
    cluster = 0
    while not movies[movies.cluster == 0].empty:
        movies_not_clustered = movies[movies.cluster == 0]
        entry = movies_not_clustered.index[0]
        movies_not_clustered['rank_log'] = distance_matrix[movies_not_clustered.loc[entry].row_index.astype('int'),
                                                           movies_not_clustered.row_index.astype('int')]
        movies_not_clustered.sort_values(by='rank_log', inplace=True)
        cluster += 1
        movies.loc[movies_not_clustered.index[:nr_movies_per_cluster], 'cluster'] = cluster
    return movies


def get_best_movies_outside_cluster(movies, cluster, random_size, distance_matrix):
    random_index = random.randint(0, random_size-1)
    movies.sort_values(by='row_index', inplace=True)
    movies['rank_log'] = np.sum(distance_matrix[:, movies[movies.cluster == cluster].row_index],
                                axis=1)
    top_movie = movies[movies.cluster != cluster].sort_values(by='rank_log').index[random_index]
    return top_movie


def get_best_movie_of_cluster_1_for_cluster_2(movies, cluster_1, cluster_2,
                                              random_size, distance_matrix):
    movies_cluster_1 = movies[movies.cluster == cluster_1]
    nr_movies_cluster_1 = movies_cluster_1.shape[0]
    movies_cluster_2 = movies[movies.cluster == cluster_2]
    distance_tmp = distance_matrix[movies_cluster_1.row_index, :]
    distance_tmp = distance_tmp[:, movies_cluster_2.row_index]
    movies_cluster_1['rank_log'] = np.sum(distance_tmp, axis=1)
    random_index = random.randint(0, min(random_size, nr_movies_cluster_1)-1)
    top_movie = movies_cluster_1.sort_values(by='rank_log').index[random_index]
    return top_movie


def cluster_algorithm_1(movies, distance_matrix):
    nr_iter = 3000
    for cnt_iter in range(nr_iter):
        movies['cluster_tmp'] = movies['cluster']
        all_clusters = movies.cluster.unique()
        cluster_1 = all_clusters[random.randint(0, len(all_clusters) - 1)]
        entry_2 = get_best_movies_outside_cluster(movies, cluster_1, random_size=int(movies.shape[0]/10),
                                                  distance_matrix=distance_matrix)
        cluster_2 = movies.loc[entry_2].cluster
        entry_1 = get_best_movie_of_cluster_1_for_cluster_2(movies, cluster_1=cluster_1, cluster_2=cluster_2,
                                                            random_size=int(5),
                                                            distance_matrix=distance_matrix)
        movies.loc[entry_1, 'cluster_tmp'] = cluster_2
        movies.loc[entry_2, 'cluster_tmp'] = cluster_1
        score_cluster_1_old = get_rank_score(movies=movies[movies.cluster == cluster_1],
                                             distance_matrix=distance_matrix)
        score_cluster_1_new = get_rank_score(movies=movies[movies.cluster_tmp == cluster_1],
                                             distance_matrix=distance_matrix)
        score_cluster_2_old = get_rank_score(movies=movies[movies.cluster == cluster_2],
                                             distance_matrix=distance_matrix)
        score_cluster_2_new = get_rank_score(movies=movies[movies.cluster_tmp == cluster_2],
                                             distance_matrix=distance_matrix)
        if (score_cluster_1_new + score_cluster_2_new) < (score_cluster_1_old + score_cluster_2_old):
            # print(movie_index.loc[[entry_1, entry_2]])
            movies['cluster'] = movies['cluster_tmp']
            # print(movie_index.loc[[entry_1, entry_2]])
            print('Iter: ' + str(cnt_iter) +
                  ' Old (partial) score:' + str(round(score_cluster_1_old + score_cluster_2_old, 2)) +
                  ' New (partial) score:' + str(round(score_cluster_1_new + score_cluster_2_new, 2)))
    return movies
