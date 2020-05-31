from django.urls import path
from movie_app.analysis import views

urlpatterns = [

    path('',
         views.Analysis.as_view(),
         name='analysis'),

    # Analysis: Histrogram of ratings per user
    # path of data (json)
    path('histogram-data/',
         views.analysis_histogram_data,
         name='analysis-histogram-data'),
]