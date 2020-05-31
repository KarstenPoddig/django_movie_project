import numpy as np
import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django_movie_project.views import OutputObject
from movie_app.models import ClusteringStatus, Rating, Cluster
from movie_app.views import get_movies
from movie_app.recommendation_models import load_data
from movie_app.views import get_top_movies_similarity
from movie_app.suggestions_actor import get_movie_suggestions_actor


class SuggestionsClusterView(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/suggestions_cluster.html'


class SuggestionsSimilarMoviesView(TemplateView):
    template_name = 'movie_app/suggestions_similar_movies.html'


class SuggestionsActorView(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/suggestions_actor.html'


def suggestions_cluster_data(request):
    user = request.user
    # check if the cluster algorithm is performed right now
    # (this is sometimes the case if this view is called shortly after rating some movies).
    # return then a corresponding message
    clustering_status = ClusteringStatus.objects.filter(user=user)[0].status
    if clustering_status == 'Pending':
        output = OutputObject(status='exception',
                              message='Your movies are clustered right now (because you added ' +
                                      'or deleted one or more of your ratings. Please wait a ' +
                                      'minute or two and try again.')
        return output.get_http_response()

    rated_movies = pd.DataFrame.from_records(
        Rating.objects.filter(user=user).values('movie_id', 'rating', 'cluster_id')
    )
    if rated_movies.empty:
        output = OutputObject(status='exception',
                              message="You didn't rate any movies yet.")
        return output.get_http_response()
    # get unique clusters (besides of not clustered movies)
    mean_ratings_clusters = rated_movies[~rated_movies.cluster_id.isna()]. \
        groupby('cluster_id')[['rating']].mean().sort_values(by='rating', ascending=False)
    cluster_ids = mean_ratings_clusters.index
    # this variable stores the movies which are already suggested
    # by suggestions from other clusters. This means two movies won't
    # be suggested by ratings from several clusters
    data_dict = {}
    already_suggested_movies = rated_movies.movie_id.unique()
    for cluster_id in cluster_ids:
        cluster_name = 'Cluster ' + str(int(cluster_id))
        cluster_dict = {}
        rated_movies_cluster = rated_movies[rated_movies.cluster_id == cluster_id]
        rating_pred_user = get_top_movies_similarity(rated_movies=rated_movies_cluster[['movie_id',
                                                                                        'rating']],
                                                     nr_movies=20,
                                                     movies_to_drop=already_suggested_movies)
        movies_cluster = get_movies(rating_pred_user.movieId)
        already_suggested_movies = np.concatenate((already_suggested_movies,
                                                   rating_pred_user.movieId.to_numpy()),
                                                  axis=None)
        movies_cluster = movies_cluster.merge(rating_pred_user, how='inner', on='movieId')
        movies_cluster.sort_values(by='rating_pred', ascending=False, inplace=True)
        movies_cluster.fillna('', inplace=True)
        movies_cluster.to_dict('records')
        movies_cluster = movies_cluster.to_dict('records')
        cluster_dict['movies'] = movies_cluster
        cluster_dict['tags'] = Cluster.objects.get(id=cluster_id).description.split(', ')
        data_dict[cluster_name] = cluster_dict
    output = OutputObject(status='normal',
                          data=data_dict)
    return output.get_http_response()


def suggestions_similar_movies_data(request):
    movieId = int(request.GET.get('movieId', ''))

    movie_similarity_matrix = load_data.load_similarity_matrix()
    df_movie_index = load_data.load_movie_index()
    df_similarity = df_movie_index
    df_movie_index = df_movie_index[df_movie_index.movieId == movieId]
    # movie is not contained in similarity matrix
    if df_movie_index.empty:
        output = OutputObject(status='exception',
                              message="The Movie you searched is unfortunately not " +
                                      "contained in the similarity list (probably " +
                                      "because there weren't enough ratings)")
        return output.get_http_response()

    df_similarity['similarity_score'] = movie_similarity_matrix[df_movie_index.row_index.iloc[0]]
    df_similarity = df_similarity.sort_values(by='similarity_score', ascending=False)[1:21]
    movies = df_similarity.merge(get_movies(df_similarity.movieId),
                                 how='inner', on='movieId')
    movies = movies.fillna('')
    movies = movies.to_dict('records')
    output = OutputObject(status='normal',
                          data=movies)
    return output.get_http_response()


def suggestions_actor_data(request):
    user = request.user
    data = get_movie_suggestions_actor(user=user)
    if len(data.keys()) == 0:
        output = OutputObject(status='exception',
                              message="You didn't rate any movies.")
    else:
        output = OutputObject(status='normal',
                              data=data)
    return output.get_http_response()
