select  g.genre
       ,avg(r.rating) avg_rating

  from  public.movie_app_rating r
       ,public.movie_app_moviegenre mg
       ,public.movie_app_genre g

 where r.user_id = -- USER_ID
   and r.movie_id = mg.movie_id
   and g."genreId" = mg.genre_id

 group by g.genre