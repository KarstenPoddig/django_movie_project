import numpy as np
import pandas as pd
from django.db import connection


# base class for performing raw sql queries
class RawSQLQuery:
    def __init__(self):
        self.cursor = connection.cursor()

    # execute query
    def execute(self, query):
        self.cursor.execute(query)

    # fetch results
    def fetchall(self):
        return self.cursor.fetchall()


"""################################################################

                    Movie Search

The following segment contains the following functions and class:

Functions: - get_genre_filter_str
           - get_year_filter_str
Class :    - QueryMovieDetails

This segment is used to fetch the nr of movies and movie details.
The class QueryMovieDetails is a sub-class of RawSQLQuery. 

################################################################"""


def get_genre_filter_str(filter_genre):
    if filter_genre == '':
        return ''
    filter_genre = filter_genre.split(',')
    genre_list = "'" + filter_genre[0] + "'"
    for genre in filter_genre[1:]:
        genre_list = genre_list + ",'" + genre + "'"
    return genre_list


def get_year_filter_str(filter_year):
    if filter_year == '':
        return ''
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


# subclass to perform the queries for the movie details
class QueryMovieDetails(RawSQLQuery):

    def __init__(self, term, filter_genre, filter_year, only_rated_movies,
                 page_number, nr_results_shown, user_id):
        # initiate replacement values
        super().__init__()
        self.term = term.lower()
        self.filter_genre = filter_genre
        self.filter_year = filter_year
        self.only_rated_movies = only_rated_movies
        self.page_number = page_number
        self.nr_results_shown = nr_results_shown
        self.user_id = user_id
        # initiate queries
        self.query_nr_results = ''
        self.query_movie_details = ''

    def build_query_nr_results(self):
        query_nr_results = \
            open('movie_app/sql_query/template_query_all_movies_nr_results.sql',
                 'r', encoding='utf-8-sig').read()
        # replacing term
        query_nr_results = query_nr_results.replace('TERM', self.term)
        # replacing genres
        if self.filter_genre != '':
            genre_filter_str = open('movie_app/sql_query/genre_filter.txt',
                                    'r', encoding='utf-8-sig').read()
            query_nr_results = query_nr_results.replace('-- GENRE_FILTER',
                                                        genre_filter_str)
            genre_list = get_genre_filter_str(self.filter_genre)
            query_nr_results = query_nr_results.replace('GENRE_LIST',
                                                        genre_list)
        # adjust query, if just to show rated movies
        if self.only_rated_movies == 1:
            rating_filter_str = open('movie_app/sql_query/rated_filter.txt',
                                     'r', encoding='utf-8-sig').read()
            query_nr_results = query_nr_results.replace('-- RATED_FILTER',
                                                        rating_filter_str)
            query_nr_results = query_nr_results.replace('-- RATING_TABLE',
                                                        ',public.movie_app_rating r')
            query_nr_results = query_nr_results.replace('-- USER_ID',
                                                        str(self.user_id))
        # filter year
        if self.filter_year != '':
            filter_year_str = open('movie_app/sql_query/year_filter.txt',
                                   'r', encoding='utf-8-sig').read()
            query_nr_results = query_nr_results.replace('-- YEAR_FILTER',
                                                        filter_year_str)
            year_list = get_year_filter_str(self.filter_year)
            query_nr_results = query_nr_results.replace('YEAR_LIST', year_list)
        self.query_nr_results = query_nr_results

    def build_query_movie_details(self):
        query_movie_details = open('movie_app/sql_query/template_query_all_movies.sql',
                                   'r', encoding='utf-8-sig').read()
        # replacing term
        query_movie_details = query_movie_details.replace('TERM', self.term)
        # replacing genres
        if self.filter_genre != '':
            genre_filter_str = open('movie_app/sql_query/genre_filter.txt',
                                    'r', encoding='utf-8-sig').read()
            query_movie_details = query_movie_details.replace('-- GENRE_FILTER', genre_filter_str)
            genre_list = get_genre_filter_str(self.filter_genre)
            query_movie_details = query_movie_details.replace('GENRE_LIST',
                                                              genre_list)
        # adjust query, if just to show rated movies
        if self.only_rated_movies == 1:
            rating_filter_str = open('movie_app/sql_query/rated_filter.txt',
                                     'r', encoding='utf-8-sig').read()
            query_movie_details = query_movie_details.replace('-- RATED_FILTER',
                                                              rating_filter_str)
            query_movie_details = query_movie_details.replace('-- RATING_TABLE',
                                                              ',public.movie_app_rating r')
            query_movie_details = query_movie_details.replace('-- USER_ID',
                                                              str(self.user_id))
        else:
            if self.user_id is None:
                query_movie_details = query_movie_details.replace('-- USER_ID',
                                                                  '-1')
            else:
                query_movie_details = query_movie_details.replace('-- USER_ID',
                                                                  str(self.user_id))

        # filter year
        if self.filter_year != '':
            filter_year_str = open('movie_app/sql_query/year_filter.txt',
                                   'r', encoding='utf-8-sig').read()
            query_movie_details = query_movie_details.replace('-- YEAR_FILTER',
                                                              filter_year_str)
            year_list = get_year_filter_str(self.filter_year)
            query_movie_details = query_movie_details.replace('YEAR_LIST',
                                                              year_list)
        # adjust offset and limit (to make the navigation possible)
        query_movie_details = query_movie_details.replace('-- LIMIT',
                                                          str(self.nr_results_shown))
        query_movie_details = query_movie_details.replace('-- OFFSET',
                                                          str((self.page_number - 1) * self.nr_results_shown))
        self.query_movie_details = query_movie_details

    def get_nr_results(self):
        self.build_query_nr_results()
        self.execute(query=self.query_nr_results)
        nr_results = self.fetchall()[0][0]
        return nr_results

    def get_movies_with_details(self):
        self.build_query_movie_details()
        self.execute(query=self.query_movie_details)
        query_result = self.fetchall()
        query_result = pd.DataFrame(query_result)
        if not query_result.empty:
            query_result.columns = ['movieId', 'title', 'year', 'production', 'country', 'urlMoviePoster',
                                    'imdbRating', 'actor', 'director', 'writer', 'rating', 'genre']
        query_result.replace(np.nan, '', inplace=True)
        query_result = query_result.to_dict('records')
        return query_result


"""#####################################################################

                   Analysis




#####################################################################"""


class AnalysisNrRatingsHistogram(RawSQLQuery):

    def __init__(self):
        super().__init__()
        self.query = open('movie_app/sql_query/query_analysis_histogram_nr_ratings.sql',
                          'r', encoding='utf-8-sig').read()

    def get_data(self):
        self.execute(query=self.query)
        return self.fetchall()
