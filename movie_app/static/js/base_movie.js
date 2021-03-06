
// Filter Functionalities

var filter_dict = {'Genre': [], 'Year': []}

var addFilter = function(type,value){
    var parent_node;
    if(type == 'Genre'){
        parent_node = document.getElementById('active_genre_filter');
    }
    if(type == 'Year'){
        parent_node = document.getElementById('active_year_filter');
    }
    if(!filter_dict[type].includes(value)){

        filter_dict[type].push(value);

        var filter_elem = document.createElement('div');
        filter_elem.setAttribute('class','filter_criterion');
        filter_elem.innerHTML = value;

        parent_node.appendChild(filter_elem);
    }
    console.log(filter_dict)
}

var clearFilter = function(){
    filter_dict['Genre'] = [];
    filter_dict['Year'] = [];

    document.getElementById('active_genre_filter').innerHTML='';
    document.getElementById('active_year_filter').innerHTML='';

    console.log(filter_dict);
}

var initFilters = function(){
    var elem_filter_genre = document.getElementById('filter_genre');
    var genre_entries = ['Adventure','Animation','Children','Comedy','Fantasy',
                        'Romance', 'Drama', 'Action', 'Crime', 'Thriller', 'Horror',
                        'Mystery','Sci-Fi','IMAX','Documentary','War','Musical','Western',
                        'Film-Noir'];
    for(var i=0;i<genre_entries.length;i++){
        var elem_a = document.createElement("a");
        elem_a.innerHTML = genre_entries[i];
        elem_a.onclick = function(){
            addFilter('Genre', this.innerHTML);
        };
        elem_filter_genre.appendChild(elem_a);
    };
    var elem_filter_year = document.getElementById('filter_year')
    var year_entries = ['1950s and earlier', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s']
    for(var i=0;i<year_entries.length;i++){
        var elem_a = document.createElement("a");
        elem_a.innerHTML = year_entries[i];
        elem_a.onclick = function(){
            addFilter('Year', this.innerHTML);
        };
        elem_filter_year.appendChild(elem_a);
    }
}

// Movie Functionalities

var createResultNavHTML = function(meta_data){
    htmlString = '';
    var last_page = Math.ceil(meta_data['nr_results_total'] / meta_data['nr_results_shown'])
    // if page_number > 1 create previous button
    if(page_number>1){
        htmlString += "<div class='button' " +
            "onclick='page_number+=(-1);getMovies(search_elem, result_elem, only_rated_movies, nr_results_shown, page_number);'>Previous</div>"
    }
    // if page_number > 1, create button with page number 1
    if(page_number > 1){
        htmlString +="<div class='button' " +
                "onclick='page_number=1;getMovies(search_elem, result_elem, only_rated_movies, nr_results_shown, page_number);'>1</div>"
    }
    if(page_number > 2){
        htmlString += " ... "
    }
    // always print actual page
    htmlString +="<div class='button' style='background-color: #4d638c; border-color: #4d638c;color: white;'>" +
         page_number +
         "</div>";

    if(page_number < last_page -1){
        htmlString += " ... "
    }
    // if page_number < last_page, create button for last page
    if(page_number < last_page){
        htmlString +="<div class='button' " +
                "onclick='page_number=" +
                last_page +
                ";getMovies(search_elem, result_elem, only_rated_movies, nr_results_shown, page_number);'>" +
                 last_page +
                 "</div>";
    }
    // page is not last page, create next-button
    if(page_number<last_page){
        htmlString += "<div class='button' " +
            "onclick='page_number+=1;getMovies(search_elem, result_elem, only_rated_movies, nr_results_shown, page_number);'>Next</div>"
    }
    return(htmlString);
};

/* this dictionary saves the association of rating buttons
and the corresponding movie. So that by clicking the rating area
the movieId for the movie can be sent with the url
*/
dict_movie_detailed = {}

var getMovies = function(search_elem, result_elem, only_rated_movies, nr_movies, page_number){
    dict_movie_detailed = {}
    $('#movie_loader').show();
    result_elem.innerHTML = '';
    var result_nav_elem_top = document.getElementById('result_nav_area_top');
    result_nav_elem_top.innerHTML = '';
    var result_nav_elem_bottom = document.getElementById('result_nav_area_bottom');
    result_nav_area_bottom.innerHTML = '';

    $.ajax({
        type: 'GET',
        url: url_movies_detail_data,
        dataType: 'json',
        cache: true,
        data: {
            'term': search_elem.value,
            'only_rated_movies': only_rated_movies,
            'nr_results_shown': nr_results_shown,
            'page_number': page_number,
            'filter_genre': filter_dict['Genre'].join(','),
            'filter_year': filter_dict['Year'].join(','),
        },
         success: function(json_result){
            // disable loading symbol
            $('#movie_loader').hide();

            console.log(json_result)

            // create navigation area
            result_nav_elem_top.innerHTML = createResultNavHTML(json_result['meta'])
            result_nav_elem_bottom.innerHTML = result_nav_area_top.innerHTML;

            result_elem.innerHTML = '';

            if(json_result['meta']['status'] == 'exception'){
                result_elem.innerHTML  = json_result['meta']['message'];
                return;
            }
            data = json_result['data']
            var htmlString = '';

            for(var i=0; i<data.length; i++){
                var obj = data[i];
                htmlString+= getMovieViewDetailed(obj)

            };
            result_elem.innerHTML += htmlString

            // setting and changing the rating
            for(var i=0; i<data.length; i++){
                var obj = data[i];
                var rating;

                if (typeof(obj.rating)=='number'){
                    rating = obj.rating;
                }
                else{
                    rating = 0;
                }

                $('#rateyo_' + obj.movieId).rateYo({
                    numStars: 5,
                    halfStar: true,
                    rating: rating
                }).on('rateyo.set', function(e, data){
                    var movieId = this.id.split("_")[1]
                    $.ajax({
                        'type': 'GET',
                        'url': url_rate_movie,
                        'data': {
                            'movieId': movieId,
                            'rating': data.rating//,
                            //'csrfmiddlewaretoken': getCookie("csrftoken")
                        },
                        success: function(){
                            if(data.rating == 0 && only_rated_movies==1){
                                getMovies(search_elem, result_elem, only_rated_movies, nr_movies, page_number);
                            }
                        }
                    });
                });
            }

         },
         error: function(){
            $('#movie_loader').hide();
            result_elem.innerHTML = 'Server Error'

         }
    });
};


var getSingleMovie = function(search_elem, result_elem){
    // show loading symbol
    result_elem.innerHTML='';
    document.getElementById('similar_movie_loader').hidden = false;

    $.ajax({
        type: 'GET',
        url: url_movies_detail_data,
        dataType: 'json',
        cache: true,
        data: {
            'term': search_elem.value,
            'only_rated_movies': 0,
            'nr_results_shown': 1,
            'page_number': 1,
            'filter_genre': '',
            'filter_year': '',
        },
         success: function(json_result){
            // disable loading symbol
            document.getElementById('similar_movie_loader').hidden = true;

            console.log(json_result)

            if(json_result['meta']['status'] == 'exception'){
                result_elem.innerHTML = json_result['meta']['message'];
            }
            else {
                obj = json_result['data'][0]
                result_elem.innerHTML = getMovieViewDetailed(obj);
                var rating;
                if (typeof(obj.rating)=='number'){
                    rating = obj.rating;
                }
                else{
                    rating = 0;
                }
                $('#rateyo_' + obj.movieId).rateYo({
                    numStars: 5,
                    halfStar: true,
                    rating: rating
                }).on('rateyo.set', function(e, data){
                    var movieId = this.id.split("_")[1]
                    $.ajax({
                        'type': 'GET',
                        'url': url_rate_movie,
                        'data': {
                            'movieId': movieId,
                            'rating': data.rating//,
                            //'csrfmiddlewaretoken': getCookie("csrftoken")
                        }
                    });
                });
                getSimilarMovies(movieId = obj.movieId);
            }
         },
         error: function(){
            result_elem.innerHTML = 'Server Error'
         }
    });
};


// This function creates the html-code for the Movie View (tabs: All Movies, Rated Movies)
var getMovieViewDetailed = function(obj){
    return (
        "<div class='movie_view_detailed_complete'>" +
            "<img src=" + obj.urlMoviePoster + " class='img_movie_view_detailed'>" +
            "<div class='movie_view_detailed_info' id=" + obj.movieId + ">" +
                "<div class ='row' style='background-color: #dee9fa;'>" +
                    "<div class='movie_title_wrapper' style='margin: 0 5px; font-weight: bold; font-size: 20px;'>" +
                        obj.title +
                    "</div>" +
                "</div>" +
                "<div class='row' style='padding: 4px 4px;'>" +
                    "<div class='col-sm-8' style='align-items: center;'>" +
                        "<p style='height: 36px; margin-top: 0px; margin-bottom: 0px;'>" + obj.year + ", " +
                                obj.country + ", " +
                                obj.production +
                         "</p>" +
                         "<p style='height: 36px; margin-top: 0px; margin-bottom: 0px;'> <b>Actors: </b>" + obj.actors + "</p>" +
                         "<p style='height: 36px; margin-top: 0px; margin-bottom: 0px;'> <b>Director: </b>" + obj.directors + "</p>" +
                         "<p style='height: 36px; margin-top: 0px; margin-bottom: 0px;'> <b>Writer: </b>" + obj.writers + "</p>" +
                         "<p style='height: 36px; margin-top: 0px; margin-bottom: 0px;'> <b>Genre: </b>" + obj.genres + "</p>" +
                    "</div>" +
                    "<div class='col-sm-4'>" +
                        "<div class='rateyo' id='rateyo_" + obj.movieId + "'></div>" +
                        "<p>Imdb-Rating: " + obj.imdbRating + "</p>" +
                    "</div>" +
                "</div>" +
             "</div>" +
        "</div>"
    )
};


var dict_movie_picture_info = {};

var getMovieShortViewElemIds = function(row, movieId){
    return {'movie_info_elem_id': 'movie_info_' + row + '_' + movieId,
            'movie_picture_elem_id': 'movie_picture_' + row + '_' + movieId}
}


var getMovieViewShort = function(obj, elem_ids, type){
    movie_info_elem_id = elem_ids['movie_info_elem_id']
    movie_picture_elem_id = elem_ids['movie_picture_elem_id']
    dict_movie_picture_info[movie_picture_elem_id] = movie_info_elem_id;
    htmlString = "<div class='suggested_movie_complete'>" +
                    "<img src=" + obj.urlMoviePoster + " class='img_suggestion' id='" + movie_picture_elem_id + "' onclick='toggleMovieInfo(this);'>" +
                    "<div class='movie_view_short_info' id='" + movie_info_elem_id +"'>" +
                        "<div class ='row' style='background-color: #dee9fa;'>" +
                            "<div class='movie_title_wrapper' style='padding: 5px 5px; font-weight: bold; font-size: 20px;'>" +
                                obj.title +
                            "</div>" +
                        "</div>" +
                        "<div style='padding: 5px 5px;'>" +
                            "EXTRA_LINE" +
                            "<p>" + obj.country + ", " + obj.year + "</p>" +
                            "<p>" + obj.runtime + " min </p>" +
                        "</div>" +
                    "</div>" +
                "</div>"
    switch(type){
        case "similarity":
            htmlString = htmlString.replace("EXTRA_LINE", "<p> Similarity Score: " +
                                                            obj.similarity_score.toFixed(2) + "</p>")
            break;
        case "prediction":
            htmlString = htmlString.replace("EXTRA_LINE", "<p> Predicted Rating: " +
                                                            obj.rating_pred.toFixed(2) + "</p>")
            break;
        case "else":
            htmlString = htmlString.replace("EXTRA_LINE", "")
    }
    return htmlString
}


var getSimilarMovies = function(movieId){

    // load similar movies
    $('#similar_movie_loader').show();
    document.getElementById('similarity_list').innerHTML = '';

    $.ajax({
        type: 'GET',
        url: url_suggestions_similar_movies_data,
        dataType: 'json',
        cache: true,
        data: {
            'movieId': movieId
        },
        success: function(json_result){
            console.log(json_result);
            if(json_result['meta']['status']=='exception'){
                document.getElementById('similarity_list').innerHTML = json_result['meta']['message']
            }
            else{
                var htmlString = ''
                htmlString = "<div class='scrollmenu'>";
                data = json_result['data']
                for(var i=0;i<data.length;i++){
                    obj = data[i];
                    elem_ids = getMovieShortViewElemIds(movieId=obj.movieId, row=1)
                    htmlString += getMovieViewShort(obj, elem_ids, type='similarity');
                }
                htmlString +=   "</div>";
                document.getElementById('similarity_list').innerHTML = htmlString;

                $('#similar_movie_loader').hide();

                movie_info_elements = document.getElementsByClassName('movie_view_short_info')
                for(var i=0; i<movie_info_elements.length; i++){
                    movie_info_elements[i].hidden = true;
                }
            }
        }
    })
}


var toggleMovieInfo = function(elem){
    movie_info_elem_id = dict_movie_picture_info[elem.id];
    movie_info_elem = document.getElementById(movie_info_elem_id);
    if(movie_info_elem.hidden == true){
        movie_info_elem.hidden = false;
    }
    else{
        movie_info_elem.hidden = true;
    }
}


var get_quality_of_profile = function(){

    $.ajax({
        type: 'GET',
        url: url_quality_of_profile,
        dataType: 'json',
        cache: true,
        success: function(json_result){

            profile_quality_elem = document.getElementById('profile_quality_status')

            profile_quality_elem.innerHTML =
                "<div class='row'>" +
                    "<div class='col-sm-11' align='center'>" +
                        "<h4 style='font-weight: bold;'>Quality of your profile</h4>" +
                    "</div>" +
                    "<div class='col-sm-1' align='right' style='height: 10px' onclick='closeQualityProfileInfo();'>" +
                        "<div class='profile_quality_close_btn'>X</div>" +
                    "</div>" +
                "</div>" +
                "<div class='row'>" +
                    "<div class=col-sm-5 style='font-size: 20px;'>" +
                        "<p>Status: "   + json_result['data']['status']          + "</p>" +
                    "</div>" +
                    "<div class=col-sm-5>" +
                        "<p>You rated " + json_result['data']['nr_rated_movies'] + " movies</p>" +
                    "</div>" +
                "</div>" +
                "<p style='padding-left: 15px;'>" + json_result['data']['note'] + "</p>";

        }
    })
}

var closeQualityProfileInfo = function(){
    var elem = document.getElementById('profile_quality_status');
    elem.hidden = true;
}


var getClusterTagView = function(tags){
    htmlString = '';
    for(var i=0; i<tags.length; i++){
        tag = tags[i];
        htmlString += "<div class='cluster_tag_elem'>" + tag + "</div>"
    }
    return htmlString
}
