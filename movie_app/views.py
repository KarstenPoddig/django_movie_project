from django.views.generic import TemplateView
from movie_app.models import Movie, Rating
from django.http import HttpResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
from movie_app.models import Genre, MovieGenre, MoviePerson, Role, Person, MoviesSimilar
import numpy as np
from django.db.models import Count, Avg
import requests


# Create your views here.

class HomeView(TemplateView):
    """View function for home page of site"""
    template_name = 'movie_app/home.html'


class TestView(TemplateView):
    """View to test functionalities"""
    template_name = 'movie_app/test.html'


class RatedMovies(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/rated_movies.html'


class AllMovies(TemplateView):
    template_name = 'movie_app/all_movies.html'


def movie_search_short(request, only_rated_movies):
    if request.is_ajax():
        q = request.GET.get('term', '')
        if only_rated_movies:
            df_rating = pd.DataFrame.from_records(Rating.objects.filter(user=request.user).values())
            movies = Movie.objects.filter(title__icontains=q, movieId__in=df_rating['movie_id'])[:10]
        else:
            movies = Movie.objects.filter(title__icontains=q)[:10]
        results = []
        for movie in movies:
            movie_json = {'movieId': movie.movieId,
                          'value': movie.title,
                          'label': movie.title + ' (Movie)'}
            results.append(movie_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def filter_movies_only_rated(user, only_rated_movies):
    if only_rated_movies:
        movie_ids = pd.DataFrame.from_records(
            Rating.objects.filter(user=user).values()
        ).movie_id
    else:
        movie_ids = pd.DataFrame.from_records(
            Movie.objects.all().values()
        ).movieId
    return pd.Index(movie_ids)


def filter_movies_term(term):
    movie_ids = pd.DataFrame.from_records(
        Movie.objects.filter(title__contains=term).values('movieId')
    )
    # result is empty
    if movie_ids.empty:
        return pd.Index([])
    return pd.Index(movie_ids.movieId)


def filter_movies_genre(filter_genre):
    genres = filter_genre.split(',')
    if filter_genre == '':
        movie_ids = pd.DataFrame.from_records(
            Movie.objects.all().values()
        ).movieId
    else:
        movie_ids = pd.DataFrame.from_records(
            MovieGenre.objects.filter(genre__genre__in=genres).values()
        ).movie_id
    return pd.Index(movie_ids)


def filter_movies_year(filter_year):
    years = filter_year.split(',')
    if filter_year == '':
        movie_ids = pd.DataFrame.from_records(
            Movie.objects.all().values()
        ).movieId
    else:
        years_list = list()
        if '1950s and earlier' in years:
            years_list += list(range(1874, 1960))
        if '1960s' in years:
            years_list += list(range(1960, 1970))
        if '1970s' in years:
            years_list += list(range(1970, 1980))
        if '1980s' in years:
            years_list += list(range(1980, 1990))
        if '1990s' in years:
            years_list += list(range(1990, 2000))
        if '2000s' in years:
            years_list += list(range(2000, 2010))
        if '2010s' in years:
            years_list += list(range(2010, 2020))
        movie_ids = pd.DataFrame.from_records(
            Movie.objects.filter(year__in=years_list).values()
        ).movieId

    return pd.Index(movie_ids)


def get_movies(movie_ids):
    movies = pd.DataFrame.from_records(
        Movie.objects.filter(movieId__in=movie_ids).values()
    )
    if movies.empty:
        movies = pd.DataFrame({'movieId': []})
    return movies


def get_genre_info(movie_ids):
    genres = pd.DataFrame.from_records(
        MovieGenre.objects.filter(movie__movieId__in=movie_ids).values('movie__movieId',
                                                                       'genre__genre')
    )
    if genres.empty:
        genres = pd.DataFrame({'movieId': [], 'genre': []})
    genres.columns = ['movieId', 'genre']
    genres = genres.groupby('movieId')['genre'].apply(', '.join).reset_index()
    return genres


def get_person_info(movie_ids):
    person = pd.DataFrame.from_records(
        MoviePerson.objects.filter(movie__movieId__in=movie_ids).values('movie__movieId',
                                                                        'role__role',
                                                                        'person__last_name',
                                                                        'person__first_name')
    )
    if person.empty:
        return pd.DataFrame({'movieId': [], 'actor': [], 'director': [], 'writer': [], 'full_name': []})
    person.columns = ['movieId', 'role', 'last_name', 'first_name']
    person.replace(np.nan, '', inplace=True)
    person['full_name'] = person['first_name'] + ' ' + person['last_name']
    person = person.groupby(['movieId', 'role'])['full_name'].apply(', '.join).reset_index()
    person = person.pivot(index='movieId', columns='role',
                          values='full_name').reset_index()
    return person


def get_rating_info(movie_ids, user):
    if user.is_anonymous:
        return pd.DataFrame({'movieId': [], 'rating': []})
    ratings = pd.DataFrame.from_records(
        Rating.objects.filter(movie__movieId__in=movie_ids,
                              user=user).values('movie__movieId', 'rating')
    )
    if ratings.empty:
        ratings = pd.DataFrame({'movieId': [], 'rating': []})
    ratings.columns = ['movieId', 'rating']
    return ratings


def get_entries(nr_results_shown, nr_results_total, page_number):
    nr_entry_start = (page_number - 1) * nr_results_shown
    nr_entry_end = min(page_number * nr_results_shown, nr_results_total)

    return range(nr_entry_start, nr_entry_end)


def movie_search_long(request):
    # Preprocessing: reading the parameters from the request
    term = request.GET.get('term', '')
    only_rated_movies = int(request.GET.get('only_rated_movies', 0))
    nr_results_shown = int(request.GET.get('nr_results_shown', 10))
    filter_genre = request.GET.get('filter_genre', '')
    filter_year = request.GET.get('filter_year', '')
    page_number = int(request.GET.get('page_number', 10))

    movie_ids_only_rated = filter_movies_only_rated(request.user, only_rated_movies)
    movie_ids_term = filter_movies_term(term)
    movie_ids_genre = filter_movies_genre(filter_genre)
    movie_ids_year = filter_movies_year(filter_year)

    movie_ids = movie_ids_only_rated.intersection(movie_ids_term)
    movie_ids = movie_ids.intersection(movie_ids_genre)
    movie_ids = movie_ids.intersection(movie_ids_year)

    nr_results_total = len(movie_ids)
    entries = get_entries(nr_results_shown, nr_results_total, page_number)
    movie_ids = movie_ids[entries]

    movies = get_movies(movie_ids)
    movies = movies.merge(get_genre_info(movie_ids),
                          how='left', on='movieId')
    movies = movies.merge(get_person_info(movie_ids),
                          how='left', on='movieId')
    movies = movies.merge(get_rating_info(movie_ids, request.user),
                          how='left', on='movieId')
    movies.replace(np.nan, '', inplace=True)
    movies = movies.to_dict('records')
    output_dict = {'meta': {'nr_results_total': nr_results_total,
                            'total_number_pages': np.ceil(nr_results_total / nr_results_shown),
                            'page_number': page_number,
                            'nr_results_shown': nr_results_shown},
                   'movies': movies}
    return HttpResponse(json.dumps(output_dict), 'application/json')


def rate_movie(request):
    movieId = request.POST.get('movieId')
    rating = float(request.POST.get('rating'))

    ratings = Rating.objects.filter(user=request.user,
                                    movie__movieId=movieId)
    # rating of 0 is interpreted as no rating
    if rating == 0:
        # one entry exists -> delete this entry
        if len(ratings) == 1:
            ratings[0].delete()
            print('delete')
        if len(ratings) > 1:
            print('Error - multiple entries found')
    else:
        # create rating entry
        if len(ratings) == 0:
            rating_entry = Rating(user=request.user,
                                  movie=Movie.objects.get(movieId=movieId),
                                  rating=rating)
            rating_entry.save()
            print('created')
        # exactly one entry found
        if len(ratings) == 1:
            rating_entry = ratings[0]
            rating_entry.rating = rating
            rating_entry.save()
            print('changed')
        # more than one entry found
        if len(ratings) > 1:
            print('Error - multiple entries found')

    return HttpResponse('Done')


class Analysis(TemplateView):
    template_name = 'movie_app/analysis.html'


class SuggestionView(TemplateView):
    template_name = 'movie_app/suggestions.html'


def similar_movies(request):
    movieId = int(request.GET.get('movieId', ''))

    movie_similarity_matrix = np.load('Analysen/rating_matrix/movie_similarity_matrix_final.npy')
    df_movie_index = pd.read_csv('Analysen/rating_matrix/movie_index.csv')
    df_similarity = df_movie_index
    df_movie_index = df_movie_index[df_movie_index.movieId == movieId]
    # movie is not contained in similarity matrix
    if df_movie_index.empty:
        print('Movie not contained')
        return HttpResponse(json.dumps({}), 'application/json')

    df_similarity['similarity_score'] = movie_similarity_matrix[df_movie_index.row_index.iloc[0]]
    df_similarity = df_similarity.sort_values(by='similarity_score', ascending=False)[1:21]
    movies = df_similarity.merge(get_movies(df_similarity.movieId),
                                 how='inner', on='movieId')
    movies = movies.to_dict('records')
    return HttpResponse(json.dumps(movies), 'application/json')


def drop_rated_movies(movies, user):
    rated_movies = pd.DataFrame.from_records(
        Rating.objects.filter(user=user).values()
    )
    movies = movies[~movies.movieId.isin(rated_movies.movie_id)]
    return movies


def get_top_movielen_movies(user, nr_movies):
    qs = Rating.objects.values('movie_id').annotate(Count('rating'), Avg('rating')) \
        .filter(rating__count__gte=50).order_by('-rating__avg')
    movies = pd.DataFrame.from_records(qs).drop('rating__count', axis=1)
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


from movie_app.recommendation_models import load_data


def get_top_movies_similarity(user, nr_movies):

    similarity_matrix = load_data.load_similarity_matrix()
    similarity_matrix = similarity_matrix**2
    movie_index = load_data.load_movie_index()
    
    ratings_user = pd.DataFrame.from_records(
        Rating.objects.filter(user=user,
                              movie__movieId__in=movie_index.row_index).values()
    )
    ratings_user = ratings_user.merge(movie_index, how='inner',
                                      left_on='movie_id', right_on='movieId')

    # build rating vector
    rating_vector = np.array(ratings_user.rating)

    # select only the relevant part of the similarity_matrix
    similarity_matrix = similarity_matrix[:, ratings_user.row_index]
    nr_relev_movies = min(20, similarity_matrix.shape[1])
    for i in range(similarity_matrix.shape[0]):
        row = similarity_matrix[i]
        similarity_matrix[i, row.argsort()[:-nr_relev_movies]] = 0
    sum_similarities = similarity_matrix.sum(axis=1)

    rating_pred = np.dot(similarity_matrix, rating_vector)/sum_similarities

    rating_pred = pd.DataFrame({'rating_pred': rating_pred})
    rating_pred.reset_index(inplace=True)
    rating_pred.columns = ['row_index', 'rating_pred']

    rating_pred = movie_index.merge(rating_pred, on='row_index',
                                    how='inner')
    rating_pred = rating_pred[['movieId', 'rating_pred']]

    # drop movies already rated
    rating_pred = drop_rated_movies(rating_pred, user)
    rating_pred.sort_values(by='rating_pred', ascending=False, inplace=True)
    rating_pred = rating_pred[:nr_movies]
    
    return rating_pred


def suggested_movies(request):
    method = request.GET.get('method', '')
    nr_movies = 100
    if method == 'movielen_rating':
        rating_pred = get_top_movielen_movies(user=request.user, nr_movies=nr_movies)

    if method == 'imdb_rating':
        rating_pred = get_top_movies_imdb(user=request.user, nr_movies=nr_movies)

    if method == 'similarity':
        rating_pred = get_top_movies_similarity(user=request.user, nr_movies=nr_movies)

    if method == 'mixed':
        movies_similarity = get_top_movies_similarity(request.user)
        movies_imdb = get_top_movies_imdb(request.user)
        movies = pd.merge(movies_similarity, movies_imdb,
                          how='inner', on='movieId')

    movies = get_movies(rating_pred.movieId)
    movies = movies.merge(rating_pred, how='inner', on='movieId')
    movies.sort_values(by='rating_pred', ascending=False, inplace=True)

    movies = movies[:20]
    movies.fillna('', inplace=True)
    print(movies)
    movies = movies.to_dict('records')

    return HttpResponse(json.dumps(movies), 'application/json')
