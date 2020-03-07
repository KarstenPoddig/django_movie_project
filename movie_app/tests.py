from django.test import TestCase
from movie_app.models import Movie, Rating
from django.contrib.auth.models import User
from movie_app.views import get_top_movies_similarity
import pandas as pd


# Create your tests here.

# test for the computation of the
class TestComputationSuggestedMovies(TestCase):
    def setUp(self):
        # create test user
        User.objects.create_user(username='testcase_user_1')

        # create another test user with one rating, doesnt work since real database is not used
        # User.objects.create_user(username='testcase_user_2')
        # testcase_user_2 = User.objects.filter(username='testcase_user_2')[0]
        # movie = Movie.objects.filter(title__contains='Heat', year=1995)[0]
        # Rating.objects.create(user=testcase_user_2,
        #                       movie=movie,
        #                       rating=3.5)

    def test_output_empty_ratings(self):
        test_user = User.objects.filter(username='testcase_user_1')[0]
        suggested_movies = get_top_movies_similarity(user=test_user,
                                                     nr_movies=20)
        self.assertTrue((suggested_movies.columns == ['movieId', 'rating_pred']).all())
        self.assertTrue(suggested_movies.shape == (0, 2))

    # test doesnt work, see above in setUp
    # def test_output_size(self):
    #     test_user = User.objects.filter(username='testcase_user_2')[0]
    #     suggested_movies = get_top_movies_similarity(user=test_user,
    #                                                  nr_movies=15)
    #     self.assertTrue(suggested_movies.shape == (15,2))
