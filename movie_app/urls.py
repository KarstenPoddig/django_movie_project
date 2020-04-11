from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('movie_search_short/<int:only_rated_movies>/', views.movie_search_short, name='movie-search-short'),
    path('movies_search_long/', views.movie_search_long, name='movie-search-long'),
    path('movies/', views.AllMovies.as_view(), name='all-movies-overview'),


    # Rated Movies
    # Detail View
    path('rated_movies/', views.RatedMovies.as_view(), name='rated-movies-overview'),

    # Short View
    # path of template page
    path('rated_movies_cluster/', views.RatedMoviesClusterView.as_view(),
         name='rated-movies-cluster'),
    # path of data (json)
    path('rated_movies_cluster_data/', views.rated_movies_cluster_data,
         name='rated-movies-cluster-data'),


    path('rate_movie/', views.rate_movie, name='rate-movie'),
    path('analysis/', views.Analysis.as_view(), name='analysis'),


    # Suggestion Views

    # Suggestions: Cluster
    # path of template page
    path('suggestions_cluster/', views.SuggestionsClusterView.as_view(),
         name='suggestions-cluster'),
    # path of data (json)
    path('suggestions_cluster_data/', views.suggestions_cluster_data,
         name='suggestions-cluster-data'),

    # Suggestions: Similar Movies
    # path of template page
    path('suggestions_similar_movies/', views.SuggestionsSimilarMoviesView.as_view(),
         name='suggestions-similar-movies'),
    # path of data (json)
    path('suggestions_similar_movies_data/', views.suggestions_similar_movies_data,
         name='suggestions-similar-movies-data'),

    # Suggestions: Actors
    # path of template page
    path('suggestions_actor/', views.SuggestionsActorView.as_view(),
         name='suggestions-actor'),
    # path of data (json)
    path('suggestions_actor_data/', views.suggestions_actor_data, name='suggestions-actor-data'),
]
