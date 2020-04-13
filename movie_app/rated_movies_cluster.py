import numpy as np
import pandas as pd
from movie_app.models import Rating


def get_rated_movies_clustered(user):
    rated_movies = pd.DataFrame.from_records(
        Rating.objects.filter(user=user).values('movie__movieId',
                                                'movie__title',
                                                'rating',
                                                'cluster',
                                                'movie__year',
                                                'movie__urlMoviePoster',
                                                'movie__country',
                                                'movie__nrRatings',
                                                'movie__runtime')
    )
    if rated_movies.empty:
        return {}
    rated_movies.columns = ['movieId', 'title', 'rating', 'cluster',
                            'year', 'urlMoviePoster', 'country', 'nrRatings',
                            'runtime']
    clusters = rated_movies.cluster.unique()
    if len(clusters) == 1 and clusters[0] is None:
        clusters[0] = np.nan
    clusters.sort()
    output_dict = {}
    for cluster in clusters:
        # compute cluster name
        if np.isnan(cluster):
            cluster_name = 'Not clustered'
            result = rated_movies[rated_movies.cluster.isna()]
        else:
            cluster_name = 'Cluster ' + str(int(cluster))
            result = rated_movies[rated_movies.cluster == cluster]
        result.sort_values(by='nrRatings', ascending=False, inplace=True)
        result.drop(axis='columns', labels=['cluster'], inplace=True)
        result.fillna('', inplace=True)
        result = result.to_dict('records')
        output_dict[cluster_name] = result
    return output_dict
