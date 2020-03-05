-- SQL for all movies
select count(*)

from public.movie_app_movie m
    -- RATING_TABLE

where 1=1
  -- filtering term
  and lower(m.title) like '%TERM%'
  -- filtering genre
  -- GENRE_FILTER
  -- RATED_FILTER
  -- YEAR_FILTER
