from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """View function for home page of site"""
    template_name = 'movie_app/home.html'


class RatedMovies(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/rated_movies.html'


class AllMovies(TemplateView):
    template_name = 'movie_app/all_movies.html'


class Analysis(LoginRequiredMixin, TemplateView):
    """This view is the template class for the Analys site. This site
    contains statistical summaries."""
    template_name = 'movie_app/analysis.html'


class SuggestionsClusterView(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/suggestions_cluster.html'


class SuggestionsSimilarMoviesView(TemplateView):
    template_name = 'movie_app/suggestions_similar_movies.html'


class SuggestionsActorView(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/suggestions_actor.html'


class RatedMoviesClusterView(LoginRequiredMixin, TemplateView):
    template_name = 'movie_app/rated_movies_cluster.html'