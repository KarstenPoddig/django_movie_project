"""#################################################################################
This file provides the data analysis results for the statistic page (only for
staff user)

#################################################################################"""

from movie_app.views.views_output_object import OutputObject
from movie_app.sql_query.sql_query import AnalysisNrRatingsHistogram


def analysis_histogram_data(request):
    histogram_data = AnalysisNrRatingsHistogram().get_data()
    output = OutputObject(status='normal',
                          data=histogram_data)
    return output.get_http_response()
