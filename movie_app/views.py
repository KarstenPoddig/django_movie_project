import json
import numpy as np
import pandas as pd
from django.http import HttpResponse
from django.db.models import Count, Avg
from movie_app.models import Movie, Rating
from movie_app.recommendation_models import load_data
from movie_app.suggestions_cluster import update_movie_clusters
from django_movie_project.views import OutputObject
from movie_app.sql_query.sql_query import QueryMovieDetails
from django.views.generic import TemplateView

"""
################### General comments ##############################################

the frame for the pages are the classes
    - HomeView ->       http://.../movie_app/
    - RatedMovies ->    http://.../movie_app/rated_movies/
    - AllMovies ->      http://.../movie_app/movies/
    - SuggestionView -> http://.../movie_app/suggestions/
    - AnalysisView ->   http://.../movie_app/analysis/
(see the file urls.py)


Philosophy / Architecture:

These classes are just empty cases. The actual contents are loaded through
jquery-requests, which then call the functions
    - movie_search_short
    - movie_search_long
    - rate_movie
    - similar_movies
    - suggested_movies 
(see the file urls.py)
These functions then return data (based on the request) in json format. 
Afterwards the passed data again is processed and shown with javascript.

The purpose of this architecture is to make the pages more dynamic (-> single
page applications). (i.e. updating only certain parts of the pages)
Otherwise the page would need to be reloaded completely and therefore be less 
dynamic.

###################################################################################
"""


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


"""############## Movie Querys #####################################################

The tabs "All Movies" and "Rated Movies" contain detailed information of the
listed movies from several tables in the database (movie, genre, actors, ratings, 
etc.). To collect these informations several join and filter operations are necessary.
Therefore, instead of using the Django ORM, a query is built with the functions 
    - build_movie_query
    - get_nr_results_movie_query
    - get_year_filter_str
    - get_genre_filter_str.
Afterwards the generated query is executed directly on the database.

There are several building blocks in the path 'movie_app/sql_query/' with which
the final query is generated. These building blocks contain placeholders which are
replaced with variables (input of build_movie_query, like LIMIT, TERM, etc.).

The tabs "All Movies" and "Rated Movies" contain the functionality to restrict
the query results to certain genres, production years or just to show rated movies.
The regarding code in the WHERE-clause of the final query is contained in the files
    - movie_app/sql_query/year_filter.txt
    - movie_app/sql_query/genre_filter.txt
    - movie_app/sql_query/rated_filter.txt

The functions build_movie_query and get_nr_results_movie_query adds the regarding
code if actual restrictions are active.

The function get_nr_results_movie_query is somehow redundant, because one could only
run the function build_movie_query and count the results. But in this situation a lot
of data would be passed (thousands of movies).
Instead the movie query is executed for collecting only the information on each page.
To compute the total number of pages of results (i.e. when movies with a certain term 
or movies of a certain genre are searched) get_nr_results_movie_query is used, so 
that the total number of pages of the result can be computed (to navigate through 
the query results).

##################################################################################"""


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


"""################# Movie Suggestions ##############################################

The class SuggestionView is the frame for the tab "Movie Suggestions".

It contains the secions
- Movie Suggestions
- Similar Movies

# Movie Suggestions

If a logged in user opens the page "Movie Suggestions" a javascript routine calls
the url suggested_movies and consequently the function "suggested_movies" (in 
this file). The result is returned in json format.
Depending on the input this function returns a list of suggested movies. There 
are several ways how the suggested movies are determined:
    - top movies based on the Movielen ratings (and therefore on this app)
    - top movies based on the imdb rating
    - personal recommendation: movies based on the similarity and ratings 
      of the regarding user. For the explanation of the algorithm  take a look 
      at the README-file (or documentation)


# Similar Movies

If the user enters a Movie in the search field a javascript routine calls the 
function "similar_movies". This function loads the similarity matrix and finds 
the most similar movies. The result is returned in json format.

###############################################################################"""


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
