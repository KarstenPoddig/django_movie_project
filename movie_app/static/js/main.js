
$('#movie_title').autocomplete({
    source: url_movie_search_short,
    minLength: 3,
})


function getCookie(c_name){
    if (document.cookie.length > 0){
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1){
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1)
                c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }

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

var getMovies = function(search_elem, result_elem, only_rated_movies, nr_movies){
    $('#movie_loader').show();
    $.ajax({
        type: 'GET',
        url: url_movie_search_long,
        dataType: 'json',
        cache: true,
        data: {
            'term': search_elem.value,
            'only_rated_movies': only_rated_movies,
            'nr_movies': nr_movies,
            'filter_genre': filter_dict['Genre'].join(','),
            'filter_year': filter_dict['Year'].join(','),
         },
         success: function(data){
            $('#movie_loader').hide();
            console.log(data);
            result_elem.innerHTML = '';

            if(data == null){
                result_elem.innerHTML  = "You didn't rate any movies yet.";
                return;
            }

            var htmlString = '';

            for(var i=0; i<data.length; i++){
                var obj = data[i];
                htmlString+= movieViewDetailed(obj)

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

         }
    });
};



var rateMovie = function(movieId,rating){
    console.log(movieId)
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
            "<div class='row'>" +
                "<div class='col-sm-2'>" +
                    "<div class='movie_poster' id='poster_" + obj.movieId + "'>" +
                    "</div>" +
                    "<img src='" + obj.urlMoviePoster + "' width='60%'>" +
                "</div>" +
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

    $.getJSON(url_similar_movies,
        {'movieId': movieId},
        function(data){
            var htmlString = ''
            htmlString = "<div class='scrollmenu'>";
            for(var i=0;i<data.length;i++){
                obj = data[i];
                htmlString += movieSimilariyView(obj);
            }
            htmlString +=   "</div>";
            document.getElementById('similarity_list').innerHTML = htmlString;
        }
    )
}


var movieSimilariyView = function(obj){
    return(
        "<div class='similarity_class'>" +
            "<p>" + obj.title + "</p>" +
            "<p>" + obj.similarity_score.toFixed(2) + "</p>" +
            "<img src=" + obj.urlMoviePoster + " width='60%'>" +
        "</div>"
    )
};

// Sidenav-menu-button
var sidenavButtonClick = function(x) {
  x.classList.toggle("change");
  $('.sidenav').toggle("change");
}

