from django.test import TestCase
from django.test import Client, RequestFactory
from movie_app.models import Movie, Rating
from django.contrib.auth.models import User
from movie_app.rated_movies.views import hist_ratings_data, \
    hist_ratings_per_genre_data, ratings_per_year_data, \
    avg_rating_per_genre_data
import json


class RatedMoviesStatisticsTest(TestCase):
    def setUp(self):
        # set up user
        self.factory = RequestFactory()

    # tests of the function hist_rating_data
    def test_hist_rating_data_empty(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/hist_ratings_data/'
        )
        request.user = User.objects.filter(username='testuser_no_ratings')[0]
        response = hist_ratings_data(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data'],
                         {'rating': [], 'nr_ratings': []})

    def test_hist_rating_data_general(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/hist_ratings_data/'
        )
        request.user = User.objects.filter(username='testuser_lt_20_ratings')[0]
        response = hist_ratings_data(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data'],
                         {'rating':     [2.0, 2.5, 3.0, 3.5, 4.0, 5.0],
                          'nr_ratings': [1,   3,   3,   1,   1,   1]})

    # tests of the function hist_ratings_per_genre_data
    def test_hist_ratings_per_genre_data_empty(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/hist_ratings_per_genre_data/'
        )
        request.user = User.objects.filter(username='testuser_no_ratings')[0]
        response = hist_ratings_per_genre_data(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data'],
                         {'genre': [],
                          'nr_ratings': []})

    def test_hist_ratings_per_genre_data_general(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/hist_ratings_per_genre_data/'
        )
        request.user = User.objects.filter(username='testuser_lt_20_ratings')[0]
        response = hist_ratings_per_genre_data(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data'],
                         {'genre': ['Comedy', 'Romance', 'Drama', 'Adventure', 'Action',
                                    'Animation', 'Children', 'Film-Noir'],
                          'nr_ratings': [7, 5, 4, 2, 1, 1, 1, 1]})

    # tests for ratings_per_year_data
    def test_ratings_per_year_data_empty(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/ratings_per_year_data/'
        )
        request.user = User.objects.filter(username='testuser_no_ratings')[0]
        response = ratings_per_year_data(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data'],
                         {'year': [],
                          'nr_ratings': []})

    def test_ratings_per_genre_data_general(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/ratings_per_year_data/'
        )
        request.user = User.objects.filter(username='testuser_lt_20_ratings')[0]
        response = ratings_per_year_data(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data'],
                         {'year': [1940, 1990, 2000],
                          'nr_ratings': [1, 5, 4]})

    # tests for avg_rating_per_genre_data
    def test_avg_rating_per_genre_data_empty(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/avg_rating_per_genre_data/'
        )
        request.user = User.objects.filter(username='testuser_no_ratings')[0]
        response = avg_rating_per_genre_data(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data'],
                         {'genre': [], 'avg_rating': []})

    def test_avg_rating_per_genre_data_general(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/avg_rating_per_genre_data/'
        )
        request.user = User.objects.filter(username='testuser_lt_20_ratings')[0]
        response = avg_rating_per_genre_data(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data'],
                         {'genre': ['Action', 'Adventure', 'Animation', 'Children',
                                    'Romance', 'Comedy', 'Drama', 'Film-Noir'],
                          'avg_rating': [4.0, 3.75, 3.5, 3.5,
                                         3.3, 3.29, 3.0, 3.0]})

