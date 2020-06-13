import json
import numpy as np
import pandas as pd
from django.http import HttpResponse
from movie_app.models import Movie, Rating
from movie_app.clustering.suggestions_cluster import update_movie_clusters
from django_movie_project.views import OutputObject
from movie_app.sql_query.sql_query import QueryMovieDetails
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """View function for home page of site"""
    template_name = 'movie_app/home.html'


class AllMovies(TemplateView):
    template_name = 'movie_app/all_movies.html'


def movie_search_short(request, only_rated_movies):
    """This function is used for the autocompletion in the movie search fields"""
    if request.is_ajax():
        term = request.GET.get('term', '')
        if only_rated_movies:
            df_rating = pd.DataFrame.from_records(Rating.objects.filter(user=request.user).values())
            movies = Movie.objects.filter(title__icontains=term,
                                          movieId__in=df_rating['movie_id'])[:10]
        else:
            movies = Movie.objects.filter(title__icontains=term)[:10]
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


def movies_detail_data(request):
    """This function collects the movie information for the tabs
     "All Movies" and "Rated Movies" and returns it as json"""

    # Preprocessing: reading the parameters from the request
    term = request.GET.get('term', '')
    term = term.replace("'", "%")
    only_rated_movies = int(request.GET.get('only_rated_movies', 0))
    nr_results_shown = int(request.GET.get('nr_results_shown', 10))
    filter_genre = request.GET.get('filter_genre', '')
    filter_year = request.GET.get('filter_year', '')
    page_number = int(request.GET.get('page_number', 1))
    # user_id = int(request.user.id)

    query_movie_details = QueryMovieDetails(term=term,
                                            filter_genre=filter_genre,
                                            filter_year=filter_year,
                                            only_rated_movies=only_rated_movies,
                                            page_number=page_number,
                                            nr_results_shown=nr_results_shown,
                                            user_id=request.user.id)
    nr_results_total = query_movie_details.get_nr_results()
    nr_pages_total = int(np.ceil(nr_results_total / nr_results_shown))
    page_number = min(nr_pages_total, page_number)
    # perform the actual query
    if nr_results_total == 0:
        output = OutputObject(status='exception',
                              message='No results found.')
    else:
        data = query_movie_details.get_movies_with_details()
        dict_additional_meta_data = {'nr_results_total': nr_results_total,
                                     'total_number_pages': np.ceil(nr_results_total / nr_results_shown),
                                     'page_number': page_number,
                                     'nr_results_shown': nr_results_shown}
        output = OutputObject(status='normal', data=data,
                              dict_additional_meta_data=dict_additional_meta_data)
    return output.get_http_response()


def rate_movie(request):
    """This function is used to set ratings of movies"""
    # Preprocessing: reading parameters from the request
    movieId = int(request.GET.get('movieId'))
    rating = float(request.GET.get('rating'))

    if rating not in [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
        return HttpResponse('rating invalid.')

    ratings = Rating.objects.filter(user=request.user,
                                    movie__movieId=movieId)

    # rating of 0 is interpreted as no rating
    if rating == 0:
        # one entry exists -> delete this entry
        if len(ratings) == 1:
            ratings[0].delete()
            update_movie_clusters(user=request.user,
                                  movieId=movieId,
                                  rating_action='deleted')
        if len(ratings) > 1:
            print('Error - multiple entries found')
    else:
        # create rating entry
        if len(ratings) == 0:
            rating_entry = Rating(user=request.user,
                                  movie=Movie.objects.get(movieId=movieId),
                                  rating=rating)
            rating_entry.save()
            update_movie_clusters(user=request.user,
                                  movieId=movieId,
                                  rating_action='created')
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


def get_movies(movie_ids):
    movies = pd.DataFrame.from_records(
        Movie.objects.filter(movieId__in=movie_ids).values()
    )
    if movies.empty:
        movies = pd.DataFrame({'movieId': []})
    return movies


def quality_of_profile(request):
    note = 'Test'

    nr_rated_movies = Rating.objects.filter(user=request.user).count()

    if nr_rated_movies < 20:
        status = 'room for improvement'
        note = "With more ratings you could get more reliable suggestions."
    if 20 <= nr_rated_movies < 40:
        status = "Almost Done!"
        note = 'Just with a few more rated movies you could get significantly better result ' + \
               'for your movie suggestions.'
    if 40 <= nr_rated_movies < 60:
        status = 'Good!'
        note = 'You already have a good basis for the movie suggestions. ' + \
               'Anyway the more movies you rate, the better the algorithms work.'
    if nr_rated_movies >= 60:
        status = 'Excellent'
        note = 'You have a great basis for the movie suggestions. ' + \
               'Anyway the more movies you rate, the better the algorithms work.'

    output = OutputObject(status='normal',
                          data={'nr_rated_movies': nr_rated_movies,
                                'status': status,
                                'note': note})
    return output.get_http_response()
