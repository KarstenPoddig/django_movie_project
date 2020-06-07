from django.urls import path
from movie_app.rated_movies import views

urlpatterns = [

    # Detail View
    path('', views.RatedMovies.as_view(),
         name='rated-movies-details'),

    # data for rating histogram
    path('statistics/hist_ratings_data/',
         views.hist_ratings_data,
         name='rated-movies-statistics-hist-ratings-data'),
    # Rated Movies - View with clusters
    # path of template page
    path('clustered/', views.RatedMoviesClusterView.as_view(),
         name='rated-movies-cluster'),
    # path of data (json)
    path('cluster_data/', views.rated_movies_cluster_data,
         name='rated-movies-cluster-data'),
    # Template page for statistics page (dashboard)
    path('statistics/',
         views.RatedMoviesStatistics.as_view(),
         name='rated-movies-statistics'),
    # data for histogram of ratings

    # data for histogram of ratings per genre
    path('statistics/hist_ratings_per_genre_data/',
         views.hist_ratings_per_genre_data,
         name='rated-movies-statistics-hist-genre-data'),
    # data for average rating per genre
    path('statistics/avg_rating_genre_data/',
         views.avg_rating_per_genre_data,
         name='avg-rating-genre-data'),
    # data for ratings per year
    path('statistics/ratings_per_year_data/',
         views.ratings_per_year_data,
         name='ratings-per-year'),
]
