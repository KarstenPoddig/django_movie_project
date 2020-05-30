"""#################################################################################
This file provides the statistics results for the page "Rated Movies - Statistics"
(only for staff user)

#################################################################################"""

import pandas as pd
from movie_app.views.views_output_object import OutputObject
from movie_app.models import Rating
from django.db.models import Count
from movie_app.sql_query.sql_query import RatedMoviesHistGenre,\
    RatedMoviesAvgGenre


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
    print(data)
    output = OutputObject(status='normal',
                          data=data)
    return output.get_http_response()
