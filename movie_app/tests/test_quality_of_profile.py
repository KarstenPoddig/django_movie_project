from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from movie_app.views import quality_of_profile
import json


class QualityOfProfileTest(TestCase):
    """This class tests the behaviour of the function
    'quality_of_profile'."""
    def setUp(self):
        self.factory = RequestFactory()

    def test_quality_of_profile_empty(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/quality_of_profile/'
        )
        request.user = User.objects.filter(username='testuser_no_ratings')[0]
        response = quality_of_profile(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data']['nr_rated_movies'], 0)
        self.assertEqual(response_dict['data']['status'], 'room for improvement')

    def test_quality_of_profile_general(self):
        request = self.factory.get(
            '/movie_app/rated_movies/statistics/quality_of_profile/'
        )
        request.user = User.objects.filter(username='testuser_lt_20_ratings')[0]
        response = quality_of_profile(request)
        response_dict = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_dict['data']['nr_rated_movies'], 10)
        self.assertEqual(response_dict['data']['status'], 'room for improvement')
