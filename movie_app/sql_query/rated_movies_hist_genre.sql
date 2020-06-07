
select g.genre
       ,count(*) nr_ratings

  from public.movie_app_rating r
       ,public.movie_app_genre g
       ,public.movie_app_moviegenre mg

 where r.user_id = -- USER_ID
   and r.movie_id = mg.movie_id
   and g."genreId" = mg.genre_id

 group by g.genre

 order by  nr_ratings desc
          ,genre asc