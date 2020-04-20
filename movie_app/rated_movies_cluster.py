import numpy as np
import pandas as pd
from movie_app.models import Rating, Cluster


def get_rated_movies_clustered(user):
    rated_movies = pd.DataFrame.from_records(
        Rating.objects.filter(user=user).values('movie__movieId',
                                                'movie__title',
                                                'rating',
                                                'cluster_id',
                                                'movie__year',
                                                'movie__urlMoviePoster',
                                                'movie__country',
                                                'movie__nrRatings',
                                                'movie__runtime')
    )
    if rated_movies.empty:
        return {}
    rated_movies.columns = ['movieId', 'title', 'rating', 'cluster_id',
                            'year', 'urlMoviePoster', 'country', 'nrRatings',
                            'runtime']
    clusters = rated_movies.cluster_id.unique()
    if len(clusters) == 1 and clusters[0] is None:
        clusters[0] = np.nan
    clusters.sort()
    output_dict = {}
    for cluster_id in clusters:
        # compute cluster name
        if np.isnan(cluster_id):
            cluster_name = 'Not clustered'
            result = rated_movies[rated_movies.cluster_id.isna()]
            tags = []
        else:
            cluster_name = 'Cluster ' + str(int(cluster_id))
            result = rated_movies[rated_movies.cluster_id == cluster_id]
            tags = Cluster.objects.get(id=cluster_id).description.split(', ')
        result.sort_values(by='nrRatings', ascending=False, inplace=True)
        result.drop(axis='columns', labels=['cluster_id'], inplace=True)
        result.fillna('', inplace=True)
        result = result.to_dict('records')
        cluster_dict = {'movies': result,
                        'tags': tags}
        output_dict[cluster_name] = cluster_dict
    return output_dict
