from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('test/', views.TestView.as_view(), name='test'),
    path('movie_search_short/<int:only_rated_movies>/', views.movie_search_short, name='movie-search-short'),
    path('movies_search_long/', views.movie_search_long, name='movie-search-long'),
    path('movies/', views.AllMovies.as_view(), name='all-movies-overview'),
    path('rated_movies/', views.RatedMovies.as_view(), name='rated-movies-overview'),
    path('rate_movie/', views.rate_movie, name='rate-movie'),
    path('analysis/', views.Analysis.as_view(), name='analysis'),
    path('suggestions/', views.SuggestionView.as_view(), name='suggestions'),
    path('similar_movies/', views.similar_movies, name='similar-movies'),
    path('suggested_movies/', views.suggested_movies, name='suggested-movies'),
]
