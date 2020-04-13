
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
    console.log(meta_data);
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


var getMovies = function(search_elem, result_elem, only_rated_movies, nr_movies, page_number){

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
                            'rating': data.rating,
                            'csrfmiddlewaretoken': getCookie("csrftoken")
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

    $.ajax({
        type: 'GET',
        url: url_movie_search_long,
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
         success: function(data){

            console.log(data['meta'])

            var obj = data['movies'][0];

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
                    'type': 'POST',
                    'url': url_rate_movie,
                    'data': {
                        'movieId': movieId,
                        'rating': data.rating,
                        'csrfmiddlewaretoken': getCookie("csrftoken")
                    }
                });
            });
            getSimilarMovies(movieId = obj.movieId);
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
                "<div class ='row' style='background-color: #dee9fa; margin-left: 0px; margin-right: 0px;'>" +
                    "<div class='movie_title_wrapper' style='margin: 0 10px; font-weight: bold; font-size: x-large;'>" +
                        obj.title +
                    "</div>" +
                "</div>" +
                "<div class='row' style='margin-left: 0px; margin-right: 0px; padding: 5px 5px;'>" +
                    "<div class='col-sm-7'>" +
                        "<p>" + obj.year + ", " +
                                obj.country + ", " +
                                obj.production +
                         "</p>" +
                         "<p> Actors: " + obj.actor + "</p>" +
                         "<p> Director: " + obj.director + "</p>" +
                         "<p> Writer: " + obj.writer + "</p>" +
                         "<p> Genre: " + obj.genre + "</p>" +
                    "</div>" +
                    "<div class='col-sm-2'>" +
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
                        "<div class ='row' style='background-color: #dee9fa;margin-right: 0px; margin-left: 0px;'>" +
                            "<div class='movie_title_wrapper' style='padding: 5px 5px; font-weight: bold; font-size: x-large;'>" +
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
        success: function(data){
            console.log(data);
            var htmlString = ''
            htmlString = "<div class='scrollmenu'>";
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
    })
}


var getMovieSuggestionsCluster = function(){

    $('#suggested_movie_loader').show();

    $.ajax({
        type: 'GET',
        url: url_suggestions_cluster_data,
        dataType: 'json',
        cache: true,
        success: function(data){
            console.log(data)
            htmlString = '';
            // catch errors
            if(Object.keys(data)[0]=="error"){
                htmlString = data["error"]
            }
            // display movie suggestions
            else{
                clusters = Object.keys(data)
                for(var i=0; i < clusters.length; i++){
                    cluster = clusters[i]
                    //console.log(data[cluster])
                    htmlString += "<h3>Cluster " + cluster + "</h3>"
                    htmlString += "<div class='scrollmenu'>";
                    for(var j=0; j<data[cluster].length; j++){
                        obj = data[cluster][j];
                        elem_ids = getMovieShortViewElemIds(movieId = obj.movieId, row=j)
                        // append movie to html
                        htmlString += getMovieViewShort(obj=obj, elem_ids=elem_ids, type='prediction');
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
                    htmlString += "<h3>" + actor + "</h3>"
                    htmlString += "<div class='scrollmenu'>";
                    for(var j=0; j<data[actor].length; j++){
                        obj = data[actor][j];
                        // append movie to dict_movie_picture_info
                        elem_ids = getMovieShortViewElemIds(movieId=obj.movieId, row=j)
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
                    //console.log(data[cluster])
                    htmlString += "<h3>" + cluster + "</h3>"
                    htmlString += "<div class='scrollmenu'>";
                    for(var j=0; j<data[cluster].length; j++){
                        obj = data[cluster][j];
                        // append movie to dict_movie_picture_info
                        elem_ids = getMovieShortViewElemIds(movieId=obj.movieId, row=j)
                        // append movie to html
                        htmlString += getMovieViewShort(obj, elem_ids, type='else');
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