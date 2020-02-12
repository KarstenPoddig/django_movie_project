from django.views.generic import TemplateView
from movie_app.models import Movie, Rating
from django.http import HttpResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
from movie_app.models import Genre, MovieGenre, MoviePerson, Role, Person, MoviesSimilar
import numpy as np
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
        Movie.objects.filter(title__contains=term).values()
    ).movieId
    return pd.Index(movie_ids)


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
    person.columns = ['movieId', 'role', 'last_name', 'first_name']
    person.replace(np.nan, '', inplace=True)
    person['full_name'] = person['first_name'] + ' ' + person['last_name']
    person = person.groupby(['movieId', 'role'])['full_name'].apply(', '.join).reset_index()
    person = person.pivot(index='movieId', columns='role',
                          values='full_name').reset_index()
    return person


def get_rating_info(movie_ids, user):
    ratings = pd.DataFrame.from_records(
        Rating.objects.filter(movie__movieId__in=movie_ids,
                              user=user).values('movie__movieId', 'rating')
    )
    if ratings.empty:
        ratings = pd.DataFrame({'movieId': [], 'rating': []})
    ratings.columns = ['movieId', 'rating']
    return ratings


def movie_search_long(request):

    ## Preprocessing: reading the parameters from the request
    term = request.GET.get('term', '')
    only_rated_movies = int(request.GET.get('only_rated_movies', 0))
    nr_movies = int(request.GET.get('nr_movies', 10))
    filter_genre = request.GET.get('filter_genre', '')
    filter_year = request.GET.get('filter_year', '')

    movie_ids_only_rated = filter_movies_only_rated(request.user, only_rated_movies)
    movie_ids_term = filter_movies_term(term)
    movie_ids_genre = filter_movies_genre(filter_genre)
    movie_ids_year = filter_movies_year(filter_year)

    movie_ids = movie_ids_only_rated.intersection(movie_ids_term)
    movie_ids = movie_ids.intersection(movie_ids_genre)
    movie_ids = movie_ids.intersection(movie_ids_year)[:nr_movies]

    movies = get_movies(movie_ids)
    movies = movies.merge(get_genre_info(movie_ids),
                          how='left', on='movieId')
    movies = movies.merge(get_person_info(movie_ids),
                          how='left', on='movieId')
    movies = movies.merge(get_rating_info(movie_ids, request.user),
                          how='left', on='movieId')
    movies.replace(np.nan, '', inplace=True)
    movies = movies.to_dict('records')
    return HttpResponse(json.dumps(movies), 'application/json')


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
    queryset = MoviesSimilar.objects.filter(baseMovie__movieId=movieId)
    df_movie = pd.DataFrame({'movieId': np.full(len(queryset), ''),
                             'title': np.full(len(queryset), ''),
                             'similarity_score': np.full(len(queryset), ''),
                             'url_movie_poster': np.full(len(queryset), '')})

    for i in range(len(queryset)):
        elem = queryset[i]
        df_movie.at[i, 'movieId'] = elem.similarMovie.movieId
        df_movie.at[i, 'title'] = elem.similarMovie.title
        df_movie.at[i, 'similarity_score'] = elem.similarity_score
        df_movie.at[i, 'urlMoviePoster'] = elem.similarMovie.urlMoviePoster
    df_movie = df_movie.to_dict('records')

    return HttpResponse(json.dumps(df_movie), 'application/json')
