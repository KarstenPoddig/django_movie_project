from django.urls import path, include
from movie_app import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('movie_search_short/<int:only_rated_movies>/', views.movie_search_short,
         name='movie-search-short'),

    ################## All Movies ########################################

    # path of template page
    path('movies/',
         views.AllMovies.as_view(),
         name='all-movies-overview'),
    # path of data json
    path('movies_detail_data/', views.movies_detail_data, name='movies-detail-data'),


    ################## Rated Movies ########################################
    # redirecting to separate urls-file for rated movies
    path('rated_movies/', include('movie_app.rated_movies.urls')),


    path('rate_movie/', views.rate_movie, name='rate-movie'),


    ################## Suggestion Views ########################################

    # redirect to separate file
    path('suggestions/',
         include('movie_app.suggestions.urls')),

    # Profile Quality
    path('quality_of_profile/', views.quality_of_profile, name='quality-of-profile'),

    ################## Analysis Views ########################################

    # redirect to separate file
    path('analysis/',
         include('movie_app.analysis.urls')),

]
