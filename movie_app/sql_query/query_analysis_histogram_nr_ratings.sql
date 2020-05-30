  select nr_ratings
         ,count(*) frequency
    from (select r.user_id
                 ,count(*) nr_ratings
            from public.movie_app_rating r
        group by r.user_id) nr_ratings_per_user
group by nr_ratings
order by nr_ratings asc