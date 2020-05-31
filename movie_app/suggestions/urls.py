from django.urls import path
from movie_app.suggestions import views

urlpatterns = [

    #
    # Suggestions based on Clusters
    # path of template page
    path('cluster/', views.SuggestionsClusterView.as_view(),
         name='suggestions-cluster'),
    # path of data (json)
    path('cluster_data/', views.suggestions_cluster_data,
         name='suggestions-cluster-data'),

    # Suggestions: Similar Movies
    # path of template page
    path('similar_movies/',
         views.SuggestionsSimilarMoviesView.as_view(),
         name='suggestions-similar-movies'),
    # path of data (json)
    path('similar_movies_data/',
         views.suggestions_similar_movies_data,
         name='suggestions-similar-movies-data'),

    # Suggestions: Actors
    # path of template page
    path('actor/',
         views.SuggestionsActorView.as_view(),
         name='suggestions-actor'),
    # path of data (json)
    path('actor_data/',
         views.suggestions_actor_data,
         name='suggestions-actor-data'),


]