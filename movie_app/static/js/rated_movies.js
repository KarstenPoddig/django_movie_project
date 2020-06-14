
var getRatedMoviesClustered = function(){

    $('#clustered_movie_loader').show();

    $.ajax({
        type: 'GET',
        url: url_rated_movies_cluster_data,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result)
            htmlString = '';
            // catch errors
            if(json_result['meta']['status'] == 'exception'){
                htmlString = json_result['meta']['message']
            }
            // display movie suggestions
            else{
                data = json_result['data']
                clusters = Object.keys(data)
                for(var i=0; i < clusters.length; i++){
                    cluster = clusters[i]
                    // tag list
                    htmlString += "<h4>" + cluster + "</h4>" +
                                  "<div class='row' align='center'>" +
                                    "<div class='cluster_tag_wrapper' align='center'>" +
                                        getClusterTagView(data[cluster]['tags']) +
                                    "</div>" +
                                  "</div>" +
                                  "<div class='scrollmenu'>";
                    for(var j=0; j<data[cluster]['movies'].length; j++){
                        movie = data[cluster]['movies'][j];
                        // append movie to dict_movie_picture_info
                        elem_ids = getMovieShortViewElemIds(movieId=movie.movieId, row=i)
                        // append movie to html
                        htmlString += getMovieViewShort(movie, elem_ids, type='else');
                    }
                    htmlString += "</div>";
                }
            }
            document.getElementById('clustered_movie_area').innerHTML = htmlString;

            $('#clustered_movie_loader').hide();

            movie_info_elements = document.getElementsByClassName('movie_view_short_info')
            for(var i=0; i<movie_info_elements.length; i++){
                movie_info_elements[i].hidden = true;
            }
        }
    })
}


var RefreshCluster = function(){

    $.ajax({
        type: 'GET',
        url: url_refresh_movies,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result);
            if(json_result['meta']['status'] == 'normal'){
                getRatedMoviesClustered();
            }
        }
    })
}