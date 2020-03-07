from django.views.generic import TemplateView
from movie_app.models import Movie, Rating
from django.http import HttpResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
from movie_app.models import Genre, MovieGenre, MoviePerson, Role, Person, MoviesSimilar
import numpy as np
from django.db.models import Count, Avg
from django.db import connection
from movie_app.recommendation_models import load_data
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


def get_entries(nr_results_shown, nr_results_total, page_number):
    nr_entry_start = (page_number - 1) * nr_results_shown
    nr_entry_end = min(page_number * nr_results_shown, nr_results_total)

    return range(nr_entry_start, nr_entry_end)


def get_year_filter_str(filter_year):
    if filter_year == '':
        return ''
    else:
        years_list = list()
        years = filter_year.split(',')
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
        return ','.join(str(year) for year in years_list)


def get_genre_filter_str(filter_genre):
    if filter_genre == '':
        return ''
    else:
        filter_genre = filter_genre.split(',')
        genre_list = "'" + filter_genre[0] + "'"
        for genre in filter_genre[1:]:
            genre_list = genre_list + ",'" + genre + "'"
        print(genre_list)
        return genre_list


def query_all_movies(term, filter_genre, filter_year, only_rated_movies,
                     page_number, nr_results_shown, user_id):
    query = open('movie_app/sql_query/template_query_all_movies.sql',
                 'r', encoding='utf-8-sig').read()
    # replacing term
    query = query.replace('TERM', term.lower())

    # replacing genres
    if filter_genre != '':
        genre_filter_str = open('movie_app/sql_query/genre_filter.txt',
                                'r', encoding='utf-8-sig').read()
        query = query.replace('-- GENRE_FILTER', genre_filter_str)
        genre_list = get_genre_filter_str(filter_genre)
        query = query.replace('GENRE_LIST', genre_list)

    # adjust query, if just to show rated movies
    if only_rated_movies == 1:
        rating_filter_str = open('movie_app/sql_query/rated_filter.txt',
                                 'r', encoding='utf-8-sig').read()
        query = query.replace('-- RATED_FILTER', rating_filter_str)
        query = query.replace('-- RATING_TABLE', ',public.movie_app_rating r')
        query = query.replace('-- USER_ID', str(user_id))
    else:
        if user_id is None:
            query = query.replace('-- USER_ID', '-1')
        else:
            query = query.replace('-- USER_ID', str(user_id))

    # filter year
    if filter_year != '':
        filter_year_str = open('movie_app/sql_query/year_filter.txt',
                               'r', encoding='utf-8-sig').read()
        query = query.replace('-- YEAR_FILTER', filter_year_str)
        year_list = get_year_filter_str(filter_year)
        query = query.replace('YEAR_LIST', year_list)

    # adjust offset and limit (to make the navigation possible)
    query = query.replace('-- LIMIT', str(nr_results_shown))
    query = query.replace('-- OFFSET', str((page_number - 1) * nr_results_shown))
    return query


def query_all_movies_nr_results(term, filter_genre, filter_year,
                                only_rated_movies, user_id):
    query = open('movie_app/sql_query/template_query_all_movies_nr_results.sql',
                 'r', encoding='utf-8-sig').read()
    # replacing term
    query = query.replace('TERM', term.lower())

    # replacing genres
    if filter_genre != '':
        genre_filter_str = open('movie_app/sql_query/genre_filter.txt',
                                'r', encoding='utf-8-sig').read()
        query = query.replace('-- GENRE_FILTER', genre_filter_str)
        genre_list = get_genre_filter_str(filter_genre)
        query = query.replace('GENRE_LIST', genre_list)

    # adjust query, if just to show rated movies
    if only_rated_movies == 1:
        rating_filter_str = open('movie_app/sql_query/rated_filter.txt',
                                 'r', encoding='utf-8-sig').read()
        query = query.replace('-- RATED_FILTER', rating_filter_str)
        query = query.replace('-- RATING_TABLE', ',public.movie_app_rating r')
        query = query.replace('-- USER_ID', str(user_id))

    # filter year
    if filter_year != '':
        filter_year_str = open('movie_app/sql_query/year_filter.txt',
                               'r', encoding='utf-8-sig').read()
        query = query.replace('-- YEAR_FILTER', filter_year_str)
        year_list = get_year_filter_str(filter_year)
        query = query.replace('YEAR_LIST', year_list)

    return query


def movie_search_long(request):
    # Preprocessing: reading the parameters from the request
    term = request.GET.get('term', '')
    only_rated_movies = int(request.GET.get('only_rated_movies', 0))
    nr_results_shown = int(request.GET.get('nr_results_shown', 10))
    filter_genre = request.GET.get('filter_genre', '')
    filter_year = request.GET.get('filter_year', '')
    page_number = int(request.GET.get('page_number', 10))

    cursor = connection.cursor()
    # compute the total number of results
    cursor.execute(query_all_movies_nr_results(term=term,
                                               filter_genre=filter_genre,
                                               filter_year=filter_year,
                                               only_rated_movies=only_rated_movies,
                                               user_id=request.user.id))
    nr_results_total = cursor.fetchone()[0]
    # perform the actual query
    cursor.execute(query_all_movies(term=term,
                                    filter_genre=filter_genre,
                                    filter_year=filter_year,
                                    only_rated_movies=only_rated_movies,
                                    page_number=page_number,
                                    nr_results_shown=nr_results_shown,
                                    user_id=request.user.id))
    movies = cursor.fetchall()
    movies = pd.DataFrame(movies)

    # if result is not empty rename the columns
    if not movies.empty:
        movies.columns = ['movieId', 'title', 'year', 'production', 'country', 'urlMoviePoster',
                          'imdbRating', 'actor', 'director', 'writer', 'rating', 'genre']
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

    movie_similarity_matrix = load_data.load_similarity_matrix()
    # movie_similarity_matrix = np.load('Analysen/rating_matrix/movie_similarity_matrix_final.npy')
    df_movie_index = load_data.load_movie_index()
    # df_movie_index = pd.read_csv('Analysen/rating_matrix/movie_index.csv')
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


def get_top_movies_similarity(user, nr_movies):
    similarity_matrix = load_data.load_similarity_matrix()
    similarity_matrix = similarity_matrix
    movie_index = load_data.load_movie_index()

    ratings_user = pd.DataFrame.from_records(
        Rating.objects.filter(user=user,
                              movie__movieId__in=movie_index.movieId).values()
    )
    # if no ratings were found -> return empty DataFrame
    if ratings_user.empty:
        return pd.DataFrame({'movieId': [], 'rating_pred': []})

    ratings_user = ratings_user.merge(movie_index, how='inner',
                                      left_on='movie_id', right_on='movieId')

    # build rating vector
    rating_vector = np.array(ratings_user.rating)

    # select only the relevant part of the similarity_matrix
    similarity_matrix = similarity_matrix[:, ratings_user.row_index]
    nr_relev_movies = min(15, similarity_matrix.shape[1])
    for i in range(similarity_matrix.shape[0]):
        row = similarity_matrix[i]
        similarity_matrix[i, row.argsort()[:-nr_relev_movies]] = 0
    sum_similarities = similarity_matrix.sum(axis=1)

    rating_pred = np.dot(similarity_matrix, rating_vector) / sum_similarities

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


def get_movies(movie_ids):
    movies = pd.DataFrame.from_records(
        Movie.objects.filter(movieId__in=movie_ids).values()
    )
    if movies.empty:
        movies = pd.DataFrame({'movieId': []})
    return movies


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
    movies = movies.to_dict('records')

    return HttpResponse(json.dumps(movies), 'application/json')
