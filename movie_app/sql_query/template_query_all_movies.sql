-- SQL for all movies
select --movie information
	m."movieId"
	,m.title
	,m."year"
	,m.production
	,m.country
	,m."urlMoviePoster"
	,m."imdbRating"
	-- person information
	--actor
	,(select string_agg(p.first_name || ' '|| p.last_name, ', ')
	   from public.movie_app_person p
		,public.movie_app_movieperson mp
	  where mp.movie_id = m."movieId"
	    and p."personId" = mp.person_id
	    and mp.role_id = 0) as actors
	-- director
	,(select string_agg(p.first_name || ' '|| p.last_name, ', ')
	   from public.movie_app_person p
		,public.movie_app_movieperson mp
	  where mp.movie_id = m."movieId"
	    and p."personId" = mp.person_id
	    and mp.role_id = 1) as directors
	-- writer
	,(select string_agg(p.first_name || ' '|| p.last_name, ', ')
	    from public.movie_app_person p
		,public.movie_app_movieperson mp
	   where mp.movie_id = m."movieId"
	     and p."personId" = mp.person_id
	     and mp.role_id = 2) as writers
	-- rating
	,(select max(r.rating)
	    from public.movie_app_rating r
	   where r.movie_id = m."movieId"
	     and r.user_id =  -- USER_ID
	 ) as rating
	 -- genre
	,(select string_agg(g.genre, ', ')
	    from public.movie_app_genre g
		,public.movie_app_moviegenre mg
	   where mg.movie_id = m."movieId"
	     and mg.genre_id = g."genreId") as genres

from public.movie_app_movie m
     -- RATING_TABLE


where 1=1
  -- filtering term
  and lower(m.title) like '%TERM%'
  -- filtering genre
  -- GENRE_FILTER
  -- YEAR_FILTER
  -- RATED_FILTER
  -- YEAR_FILTER
  --and m.year in (1995,1994,2001,2002,2003) -- YEAR_LIST


order by m."nrRatings" desc

offset -- OFFSET
limit -- LIMIT