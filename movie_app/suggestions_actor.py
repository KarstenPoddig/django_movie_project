from movie_app.models import Rating, MoviePerson, Person
import pandas as pd


def get_movie_suggestions_actor(user):
    rated_movies = pd.DataFrame.from_records(
        Rating.objects.filter(user=user).values('movie__movieId',
                                                'movie__title',
                                                'movie__year',
                                                'movie__nrRatings',
                                                'rating')
    )
    if rated_movies.empty:
        return {}
    movies_with_actors = pd.DataFrame.from_records(
        MoviePerson.objects.filter(movie__movieId__in=rated_movies.movie__movieId,
                                   role_id=0).values('movie__movieId', 'person__personId')
    )
    movies_with_actors = pd.merge(rated_movies, movies_with_actors,
                                  how='inner', on='movie__movieId')
    actors = movies_with_actors.groupby('person__personId').agg({'rating': ['count', 'mean']})
    actors.columns = ['nr_rated_movies', 'mean_rating']
    actors = actors[actors.nr_rated_movies >= 3].sort_values(by='mean_rating', ascending=False)[:5]
    actors_info = pd.DataFrame.from_records(
        Person.objects.filter(personId__in=actors.index).values()
    ).set_index('personId')
    output_dict = {}
    for personId in actors_info.index:
        entry = actors_info.loc[personId]
        full_name = entry.first_name + ' ' + entry.last_name
        suggested_movies_actor = get_most_watched_movies_of_actor(personId=personId,
                                                                  nr_movies=20,
                                                                  ignore_movieId=rated_movies.movie__movieId)
        suggested_movies_actor = suggested_movies_actor.to_dict('records')
        output_dict[full_name] = suggested_movies_actor
    return output_dict


def get_most_watched_movies_of_actor(personId,nr_movies, ignore_movieId):
    movies = pd.DataFrame.from_records(
        MoviePerson.objects.filter(person_id=personId,
                                   role_id=0).values('movie__movieId',
                                                     'movie__title',
                                                     'movie__year',
                                                     'movie__country',
                                                     'movie__nrRatings',
                                                     'movie__urlMoviePoster',
                                                     'movie__runtime')
    )
    movies.columns = ['movieId', 'title', 'year', 'country', 'nrRatings',
                      'urlMoviePoster', 'runtime']
    movies.fillna('', inplace=True)
    movies = movies[~movies.movieId.isin(ignore_movieId)].sort_values(by='nrRatings',
                                                                      ascending=False)[:nr_movies]
    return movies