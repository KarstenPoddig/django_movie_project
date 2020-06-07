from django.test import TestCase
from movie_app.models import Movie, Rating
from django.contrib.auth.models import User

#
# class RatingModelTests(TestCase):
#     def setUp(self):
#         user = User.objects.create(username='testuser_1')
#         movie = Movie.objects.create(movieId=1, imdbId=1,
#                                      title='testmovie_1', year=1988)
#         Rating.objects.create(user=user, movie=movie, rating=5.0)
#
#     def test_rating_equal(self):
#         rating = Rating.objects.filter(user__username='testuser_1',
#                                        movie__title='testmovie_1')[0].rating
#         self.assertEqual(rating, 5.0)
#
