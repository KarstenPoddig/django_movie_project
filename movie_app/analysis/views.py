"""#################################################################################
This file provides the data analysis results for the statistic page (only for
staff user)

#################################################################################"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django_movie_project.views import OutputObject
from movie_app.sql_query.sql_query import AnalysisNrRatingsHistogram


class Analysis(LoginRequiredMixin, TemplateView):
    """This view is the template class for the Analys site. This site
    contains statistical summaries."""
    template_name = 'movie_app/analysis.html'


def analysis_histogram_data(request):
    histogram_data = AnalysisNrRatingsHistogram().get_data()
    output = OutputObject(status='normal',
                          data=histogram_data)
    return output.get_http_response()
