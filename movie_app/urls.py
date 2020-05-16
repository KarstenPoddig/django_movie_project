from django.urls import path, include
from movie_app.views import views_page_templates, views, views_analysis

urlpatterns = [
    path('', views_page_templates.HomeView.as_view(), name='home'),
    path('movie_search_short/<int:only_rated_movies>/', views.movie_search_short,
         name='movie-search-short'),

    ################## All Movies ########################################

    # path of template page
    path('movies/', views_page_templates.AllMovies.as_view(), name='all-movies-overview'),
    # path of data json
    path('movies_detail_data/', views.movies_detail_data, name='movies-detail-data'),

    # Rated Movies
    # Detail View
    path('rated_movies/', views_page_templates.RatedMovies.as_view(), name='rated-movies-overview'),

    # Short View
    # path of template page
    path('rated_movies_cluster/', views_page_templates.RatedMoviesClusterView.as_view(),
         name='rated-movies-cluster'),
    # path of data (json)
    path('rated_movies_cluster_data/', views.rated_movies_cluster_data,
         name='rated-movies-cluster-data'),

    path('rate_movie/', views.rate_movie, name='rate-movie'),
    path('analysis/', views_page_templates.Analysis.as_view(), name='analysis'),


    ################## Suggestion Views ########################################

    # Suggestions: Cluster
    # path of template page
    path('suggestions_cluster/', views_page_templates.SuggestionsClusterView.as_view(),
         name='suggestions-cluster'),
    # path of data (json)
    path('suggestions_cluster_data/', views.suggestions_cluster_data,
         name='suggestions-cluster-data'),

    # Suggestions: Similar Movies
    # path of template page
    path('suggestions_similar_movies/', views_page_templates.SuggestionsSimilarMoviesView.as_view(),
         name='suggestions-similar-movies'),
    # path of data (json)
    path('suggestions_similar_movies_data/', views.suggestions_similar_movies_data,
         name='suggestions-similar-movies-data'),

    # Suggestions: Actors
    # path of template page
    path('suggestions_actor/', views_page_templates.SuggestionsActorView.as_view(),
         name='suggestions-actor'),
    # path of data (json)
    path('suggestions_actor_data/', views.suggestions_actor_data, name='suggestions-actor-data'),

    # Profile Quality
    path('quality_of_profile/', views.quality_of_profile, name='quality-of-profile'),

    ################## Analysis Views ########################################

    # path of template page
    path('analysis', views_page_templates.Analysis.as_view(), name='analysis'),

    # Analysis: Histrogram of ratings per user
    # path of data (json)
    path('analysis-histogram-data/', views_analysis.analysis_histogram_data,
         name='analysis-histogram-data'),
]
