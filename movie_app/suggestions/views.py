import numpy as np
import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django_movie_project.views import OutputObject
from movie_app.models import ClusteringStatus, Rating, Cluster, \
    MoviePerson, Person, Movie
from movie_app.views import get_movies
from movie_app.recommendation_models import load_data


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


def get_movie_suggestions_actor(user):
    rated_movies = pd.DataFrame.from_records(
        Rating.objects.filter(user=user).values('movie__movieId',
                                                'movie__title',
                                                'movie__year',
                                                'movie__nrRatings',
                                                'rating')
    )
    if rated_movies.empty:
        return {}
    movies_with_actors = pd.DataFrame.from_records(
        MoviePerson.objects.filter(movie__movieId__in=rated_movies.movie__movieId,
                                   role_id=0).values('movie__movieId', 'person__personId')
    )
    movies_with_actors = pd.merge(rated_movies, movies_with_actors,
                                  how='inner', on='movie__movieId')
    actors = movies_with_actors.groupby('person__personId').agg({'rating': ['count', 'mean']})
    actors.columns = ['nr_rated_movies', 'mean_rating']
    actors = actors[actors.nr_rated_movies >= 3].sort_values(by='mean_rating', ascending=False)[:5]
    actors_info = pd.DataFrame.from_records(
        Person.objects.filter(personId__in=actors.index).values()
    ).set_index('personId')
    output_dict = {}
    for personId in actors_info.index:
        entry = actors_info.loc[personId]
        full_name = entry.first_name + ' ' + entry.last_name
        suggested_movies_actor = get_most_watched_movies_of_actor(personId=personId,
                                                                  nr_movies=20,
                                                                  ignore_movieId=rated_movies.movie__movieId)
        suggested_movies_actor = suggested_movies_actor.to_dict('records')
        output_dict[full_name] = suggested_movies_actor
    return output_dict


def get_most_watched_movies_of_actor(personId,nr_movies, ignore_movieId):
    movies = pd.DataFrame.from_records(
        MoviePerson.objects.filter(person_id=personId,
                                   role_id=0).values('movie__movieId',
                                                     'movie__title',
                                                     'movie__year',
                                                     'movie__country',
                                                     'movie__nrRatings',
                                                     'movie__urlMoviePoster',
                                                     'movie__runtime')
    )
    movies.columns = ['movieId', 'title', 'year', 'country', 'nrRatings',
                      'urlMoviePoster', 'runtime']
    movies.fillna('', inplace=True)
    movies = movies[~movies.movieId.isin(ignore_movieId)].sort_values(by='nrRatings',
                                                                      ascending=False)[:nr_movies]
    return movies


def drop_rated_movies(movies, movies_to_drop):
    movies = movies[~movies.movieId.isin(movies_to_drop)]
    return movies


def get_top_movielen_movies(user, nr_movies):
    query_result = Rating.objects.values('movie_id').annotate(Count('rating'), Avg('rating')) \
        .filter(rating__count__gte=50).order_by('-rating__avg')
    movies = pd.DataFrame.from_records(query_result).drop('rating__count', axis=1)
    movies.columns = ['movieId', 'rating_pred']
    movies = drop_rated_movies(movies, user)
    movies = movies[:nr_movies]
    return movies


def get_top_movies_imdb(user, nr_movies):
    movies = pd.DataFrame.from_records(
        Movie.objects.all().order_by('-imdbRating').values('movieId', 'imdbRating')
    )
    movies.columns = ['movieId', 'rating_pred']
    movies.dropna(axis=0, inplace=True)
    movies = drop_rated_movies(movies, user)
    movies = movies[:nr_movies]
    return movies


def get_top_movies_similarity(rated_movies, nr_movies, movies_to_drop):
    similarity_matrix = load_data.load_similarity_matrix()
    similarity_matrix = similarity_matrix
    movie_index = load_data.load_movie_index()

    rated_movies = rated_movies.merge(movie_index, how='inner',
                                      left_on='movie_id', right_on='movieId')

    # build rating vector
    rating_vector = np.array(rated_movies.rating)

    # select only the relevant part of the similarity_matrix
    similarity_matrix = similarity_matrix[:, rated_movies.row_index]

    # transform similarity matrix if number of rated movies is greater than 15
    nr_relev_movies = min(15, similarity_matrix.shape[1])
    if similarity_matrix.shape[1] > 15:
        for i in range(similarity_matrix.shape[0]):
            row = similarity_matrix[i]
            similarity_matrix[i, row.argsort()[:-nr_relev_movies]] = 0

    sum_similarities = similarity_matrix.sum(axis=1)
    rating_pred = np.dot(similarity_matrix, rating_vector) / sum_similarities

    # compute score for suggestions
    score_rating = rating_pred/5.0
    score_similarity = sum_similarities/nr_relev_movies

    score = 0.5*score_similarity + 0.5*score_rating

    rating_pred = pd.DataFrame({'rating_pred': rating_pred,
                                'score': score})
    rating_pred.reset_index(inplace=True)
    rating_pred.columns = ['row_index', 'rating_pred', 'score']

    rating_pred = movie_index.merge(rating_pred, on='row_index',
                                    how='inner')
    rating_pred = rating_pred[['movieId', 'rating_pred', 'score']]

    # drop movies already rated
    rating_pred = drop_rated_movies(movies=rating_pred,
                                    movies_to_drop=movies_to_drop)
    rating_pred.sort_values(by='score', ascending=False, inplace=True)
    rating_pred = rating_pred[:nr_movies]
    rating_pred.sort_values(by='rating_pred', ascending=False, inplace=True)

    return rating_pred

