-- SQL for rated movies

select --movie information
	m."movieId"
	,m.title
	,m."year"
	,m.production
	,m.country
	,m."urlMoviePoster"
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
	,r.rating
	 -- genre
	,(select string_agg(g.genre, ', ')
	    from public.movie_app_genre g
		,public.movie_app_moviegenre mg
	   where mg.movie_id = m."movieId"
	     and mg.genre_id = g."genreId") as genres

from public.movie_app_movie m
     ,public.movie_app_rating r

where 1=1
  -- joining movie and rating table
  and m."movieId" = r.movie_id
  -- filtering for user
  and r.user_id = 162542
  -- filtering term
  and lower(m.title) like '%%' -- TERM
  -- filtering genre
  and m."movieId" in (select m2."movieId"
			from public.movie_app_movie m2
			     ,public.movie_app_genre g2
			     ,public.movie_app_moviegenre mg2
		       where m2."movieId" = mg2.movie_id
		         and mg2.genre_id = g2."genreId")
		         --and g2.genre in ('Animation')) -- GENRE_LIST
  -- filtering year
  --and m.year in (1995,1994,2001,2002,2003) -- YEAR_LIST


order by r.rating desc

offset 0 -- OFFSET
limit 20 -- LIMIT