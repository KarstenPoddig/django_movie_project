var getMovieSuggestionsCluster = function(){

    $('#suggested_movie_loader').show();

    $.ajax({
        type: 'GET',
        url: url_suggestions_cluster_data,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result)
            htmlString = '';
            // catch errors
            if(json_result['meta']['status']=='exception'){
                htmlString = json_result['meta']['message']
            }
            // display movie suggestions
            else{
                data = json_result['data']
                clusters = Object.keys(data)
                for(var i=0; i < clusters.length; i++){
                    cluster = clusters[i]
                    //console.log(data[cluster])
                    htmlString += "<h4>" + cluster + "</h4>" +
                                  "<div class='row' align='center'>" +
                                    "<div class='cluster_tag_wrapper' align='center'>" +
                                        getClusterTagView(data[cluster]['tags']) +
                                    "</div>" +
                                  "</div>" +
                                  "<div class='scrollmenu'>";
                    for(var j=0; j<data[cluster]['movies'].length; j++){
                        movie = data[cluster]['movies'][j];
                        elem_ids = getMovieShortViewElemIds(movieId = movie.movieId, row=i)
                        // append movie to html
                        htmlString += getMovieViewShort(obj=movie, elem_ids=elem_ids, type='prediction');
                    }
                    htmlString += "</div>";
                }
            }
            document.getElementById('suggested_movie_cluster_area').innerHTML = htmlString;

            $('#suggested_movie_loader').hide();

            movie_info_elements = document.getElementsByClassName('movie_view_short_info')
            for(var i=0; i<movie_info_elements.length; i++){
                movie_info_elements[i].hidden = true;
            }
        }
    });
}


var getMovieSuggestionsActor = function(){

    $('#suggested_movie_loader').show();

    $.ajax({
        type: 'GET',
        url: url_suggestions_actor_data,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result)
            htmlString = '';
            // catch errors
            if(json_result['meta']['status']=='exception'){
                htmlString = json_result['meta']['message']
            }
            // display movie suggestions
            else{
                data = json_result['data']
                actors = Object.keys(data)
                for(var i=0; i < actors.length; i++){
                    actor = actors[i]
                    //console.log(data[cluster])
                    htmlString += "<h4>" + actor + "</h4>"
                    htmlString += "<div class='scrollmenu'>";
                    for(var j=0; j<data[actor].length; j++){
                        obj = data[actor][j];
                        // append movie to dict_movie_picture_info
                        elem_ids = getMovieShortViewElemIds(movieId=obj.movieId, row=i)
                        // append movie to html
                        htmlString += getMovieViewShort(obj, elem_ids, type='else');
                    }
                    htmlString += "</div>";
                }
            }
            document.getElementById('suggested_movie_cluster_area').innerHTML = htmlString;

            $('#suggested_movie_loader').hide();

            movie_info_elements = document.getElementsByClassName('movie_view_short_info')
            for(var i=0; i<movie_info_elements.length; i++){
                movie_info_elements[i].hidden = true;
            }
        }
    });
}

