from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from movie_app.models import Movie, Rating
import json
from movie_app.views import rate_movie


class RateMovie(TestCase):
    """This class tests whether the functions which set, change and
    delete the ratings are working correctly.
    For 'testuser_2' ratings are created (movieId=2) and
    deleted (movieId=5). In the setUp the rating for the movieId=5 is set."""
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.filter(username='testuser_2')[0]
        # delete rating (if existing)
        Rating.objects.filter(user__username='testuser_2',
                              movie__movieId=2).delete()
        # create rating for
        Rating.objects.create(user=self.user,
                              movie=Movie.objects.get(movieId=5),
                              rating=5.0)

    def test_create_rating(self):
        # rate movie
        request = self.factory.get(
            'movie_app/rate_movie/',
            {'movieId': 2,
             'rating': 3.5}
        )
        request.user = self.user
        rate_movie(request)
        # check if rating exists
        rating = Rating.objects.filter(user=self.user,
                                       movie__movieId=2)[0]
        self.assertEqual(rating.rating, 3.5)

    def test_drop_rating(self):
        request = self.factory.get(
            'movie_app/rate_movie/',
            {'movieId': 5,
             'rating': 0.0}
        )
        request.user = self.user
        # drop rating (0 should be interpreted as not rated)
        rate_movie(request)
        # check if rating exists (number of query results should be 0)
        self.assertEqual(0, len(Rating.objects.filter(user=self.user,
                                                      movie__movieId=5)))

    # test rejection of rating, if rating has not a valid value
    def test_rate_movie_invalid_value(self):
        # rate movie
        request = self.factory.get(
            'movie_app/rate_movie/',
            {'movieId': 6,
             'rating': 3.65}
        )
        request.user = self.user
        response = rate_movie(request)
        self.assertEqual(response.content.decode('utf-8'),
                         'rating invalid.')
        self.assertEqual(len(Rating.objects.filter(user=self.user,
                                                   movie__movieId=6)),
                         0)
