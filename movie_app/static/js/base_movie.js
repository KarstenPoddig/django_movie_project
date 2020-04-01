
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
        url: url_movie_search_long,
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
         success: function(data){
            // disable loading symbol
            $('#movie_loader').hide();

            console.log(data)

            // create navigation area
            result_nav_elem_top.innerHTML = createResultNavHTML(data['meta'])
            result_nav_elem_bottom.innerHTML = result_nav_area_top.innerHTML;

            console.log(data['meta'])

            //
            result_elem.innerHTML = '';

            if(data == null){
                result_elem.innerHTML  = "You didn't rate any movies yet.";
                return;
            }

            var htmlString = '';

            for(var i=0; i<data['movies'].length; i++){
                var obj = data['movies'][i];
                htmlString+= movieViewDetailed(obj)

            };
            result_elem.innerHTML += htmlString

            // setting and changing the rating
            for(var i=0; i<data['movies'].length; i++){
                var obj = data['movies'][i];
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
                        },
                        success: function(){
                            if(data.rating == 0){
                                getMovies(search_elem, result_elem, only_rated_movies, nr_movies);
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

            result_elem.innerHTML = movieViewDetailed(obj);

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
var movieViewDetailed = function(obj){

    return (
        "<div class='movie_class' id=" + obj.movieId + ">" +
            "<div class ='row' style='background-color: #dee9fa'>" +
                "<div class='movie_title_wrapper' style='margin: 0 10px; font-weight: bold; font-size: x-large;'>" +
                    obj.title +
                "</div>" +
            "</div>" +
            "<div class='row' style='padding-top: 5px; padding: 5px;'>" +
                "<img src='" + obj.urlMoviePoster + "' height=200px>" +
                "<div class='col-sm-6'>" +
                    "<p>" + obj.year + ", " +
                            obj.country + ", " +
                            obj.production +
                     "</p>" +
                     "<p> Actors: " + obj.actor + "</p>" +
                     "<p> Director: " + obj.director + "</p>" +
                     "<p> Writer: " + obj.writer + "</p>" +
                     "<p> Genre: " + obj.genre + "</p>" +
                "</div>" +
                "<div class='col-sm-4'>" +
                    "<div class='rateyo' id='rateyo_" + obj.movieId + "'></div>" +
                    "<p>Imdb-Rating: " + obj.imdbRating + "</p>" +
                "</div>" +
            "</div>" +
         "</div>"
    )
};

var getSimilarMovies = function(movieId){

    // load similar movies
    $('#similar_movie_loader').show();
    document.getElementById('similarity_list').innerHTML = '';

    $.getJSON(url_similar_movies,
        {'movieId': movieId},
        function(data){
            console.log(data);
            var htmlString = ''
            htmlString = "<div class='scrollmenu'>";
            for(var i=0;i<data.length;i++){
                obj = data[i];
                htmlString += movieSimilarityView(obj);
            }
            htmlString +=   "</div>";
            document.getElementById('similarity_list').innerHTML = htmlString;

            $('#similar_movie_loader').hide();
        }
    )
}


var movieSimilarityView = function(obj){
    return(
        "<div class='similarity_class'>" +
            "<div class ='row' style='background-color: #dee9fa'>" +
                "<div class='movie_title_wrapper' style='margin: 0 10px; font-weight: bold; font-size: x-large;'>" +
                    obj.title +
                "</div>" +
            "</div>" +
            "<p> Similarity Score: " + obj.similarity_score.toFixed(2) + "</p>" +
            "<img src=" + obj.urlMoviePoster + " width='60%'>" +
        "</div>"
    )
};

var getMovieSuggestions = function(method){

    // load movie suggestions
    $('#suggested_movie_loader').show();

    $.ajax({
        type: 'GET',
        url: url_suggested_movies,
        dataType: 'json',
        cache: true,
        data: {
            'method': method,
        },
        success: function(data){
            console.log(data);
            var htmlString = ''
            htmlString = "<div class='scrollmenu'>";
            for(var i=0;i<data.length;i++){
                obj = data[i];
                htmlString += suggestedMovieView(obj);
            }
            htmlString +=   "</div>";
            document.getElementById('suggested_movies_list').innerHTML = htmlString;

            $('#suggested_movie_loader').hide();
        },
        error: function(e){
            console.log(e)
        }
    });
}


var suggestedMovieView = function(obj){
    return(
        "<div class='similarity_class'>" +
            "<div class ='row' style='background-color: #dee9fa'>" +
                "<div class='movie_title_wrapper' style='margin: 0 10px; font-weight: bold; font-size: x-large;'>" +
                    obj.title +
                "</div>" +
            "</div>" +
            "<p> Expected Rating: " + obj.rating_pred.toFixed(2) + "</p>" +
            "<img src=" + obj.urlMoviePoster + " width='60%'>" +
        "</div>"
    )
}

var getMovieSuggestionsCluster = function(){

    $.ajax({
        type: 'GET',
        url: url_suggested_movies_cluster,
        dataType: 'json',
        cache: true,
        success: function(data){
            console.log(data)
        }
    });
}