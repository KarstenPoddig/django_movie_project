from django.db import models


# Create your models here.

class Movie(models.Model):
    """Model representing a Movie"""
    movieId = models.IntegerField(primary_key=True)
    imdbId = models.IntegerField()
    title = models.CharField(max_length=200)
    year = models.IntegerField(blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)
    production = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    imdbRating = models.FloatField(blank=True, null=True)
    urlMoviePoster = models.CharField(max_length=200, null=True, default=None)
    nrRatings = models.IntegerField(null=True)

    def __str__(self):
        return self.title


class Genre(models.Model):
    """Model representing a Genre"""
    genreId = models.IntegerField(primary_key=True)
    genre = models.CharField(max_length=50)


class Person(models.Model):
    personId = models.IntegerField(primary_key=True)
    last_name = models.CharField(max_length=50, null=True)
    first_name = models.CharField(max_length=50, null=True)

    def __str__(self):
        name = ''
        if not (self.last_name is None):
            name += self.last_name
        if not (self.first_name is None):
            name += (', ' + self.first_name)
        return name


class Role(models.Model):
    """Model saving the role in movies like actor, writer, etc"""
    roleId = models.IntegerField(primary_key=True)
    role = models.CharField(max_length=20)


class MoviePerson(models.Model):
    """Model which people worked in which role on a movie"""
    movie = models.ForeignKey('Movie', on_delete=models.SET_NULL, null=True)
    person = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True)


class MovieGenre(models.Model):
    """"Model saves the association of a movie to a genre"""
    movie = models.ForeignKey('Movie', on_delete=models.SET_NULL, null=True)
    genre = models.ForeignKey('Genre', on_delete=models.SET_NULL, null=True)


class Language(models.Model):
    """Model saves the Languages in movies"""
    languageId = models.IntegerField(primary_key=True)
    language = models.CharField(max_length=50)


class MovieLanguage(models.Model):
    """Model saves the association of a movie to a language"""
    movie = models.ForeignKey('Movie', on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)


from django.contrib.auth.models import User


class Rating(models.Model):
    """Model saves the ratings of users"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    movie = models.ForeignKey('Movie', on_delete=models.SET_NULL, null=True)
    rating = models.FloatField()
    cluster = models.IntegerField(null=True)


class MoviesSimilar(models.Model):
    """Model saves the similarity scores (of the top movies)"""
    baseMovie = models.ForeignKey(Movie, related_name='baseMovie', on_delete=models.SET_NULL, null=True)
    similarMovie = models.ForeignKey(Movie, related_name='similarMovie', on_delete=models.SET_NULL, null=True)
    similarity_score = models.FloatField()

