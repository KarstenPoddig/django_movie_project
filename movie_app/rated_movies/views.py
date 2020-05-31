import pandas as pd
from movie_app.models import Rating
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django_movie_project.views import OutputObject
from movie_app.sql_query.sql_query import RatedMoviesHistGenre,\
    RatedMoviesAvgGenre
from movie_app.rated_movies.rated_movies_cluster import get_rated_movies_clustered


class RatedMovies(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/rated_movies.html'


class RatedMoviesClusterView(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/rated_movies_cluster.html'


class RatedMoviesStatistics(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/rated_movies_statistics.html'


def hist_ratings_data(request):
    data = \
        pd.DataFrame.from_records(
            Rating.objects.filter(user=request.user).values('rating')
                .annotate(Count('movie_id'))
        ).to_dict('list')
    # rename column 'movie_id__count' to 'nr_ratings'
    data['nr_ratings'] = data.pop('movie_id__count')
    output = OutputObject(status='normal',
                          data=data)
    return output.get_http_response()


def hist_ratings_per_genre_data(request):
    query_obj = RatedMoviesHistGenre()
    query_obj.build_query(user_id=request.user.id)
    data = query_obj.get_data()
    output = OutputObject(status='normal',
                          data=data)
    return output.get_http_response()


def avg_rating_per_genre_data(request):
    query_obj = RatedMoviesAvgGenre()
    query_obj.build_query(user_id=request.user.id)
    data = query_obj.get_data()
    output = OutputObject(status='normal',
                          data=data)
    return output.get_http_response()


def rated_movies_cluster_data(request):
    user = request.user
    data = get_rated_movies_clustered(user=user)
    if len(data.keys()) == 0:
        output = OutputObject(status='execption',
                              message="You didn't rate any movies.")
    else:
        output = OutputObject(status='normal',
                              data=data)
    return output.get_http_response()
