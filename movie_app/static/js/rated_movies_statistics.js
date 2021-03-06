

//------------------- Histogram - Ratings -------------------------------------------

var hist_ratings_data = {
    labels: [],
    datasets: [{
        label: 'Ratings',
        backgroundColor: '#dddddd',
        borderWidth: 1,
        data: [] //[1, 3, 1, 5, 5, 1, 4, 6, 9, 3]
    }]
};

var ctx_histogram_ratings = document.getElementById('hist_ratings').getContext('2d');
var hist_ratings = new Chart(ctx_histogram_ratings, {
    type: 'bar',
    data: hist_ratings_data,
    options: {
        responsive: true,
        legend: {
            position: 'top'
        },
        scales: {
            yAxes: [{
                ticks: {
                    min: 0
                }
            }]
        }
    }
});

var getHistRatings = function(){

    $.ajax({
        type: 'GET',
        url: url_rated_movies_statistics_hist_ratings_data,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result)
            hist_ratings.data.labels = json_result['data']['rating'];
            hist_ratings.data.datasets[0].data = json_result['data']['nr_ratings'];
            hist_ratings.update();
        }
    });
};

//------------------- Histogram - Genres -------------------------------------------

var hist_genre_data = {
    labels: [],
    datasets: [{
        label: 'Ratings',
        backgroundColor: '#dddddd',
        borderWidth: 1,
        data: []
    }]
}

var ctx_hist_genre = document.getElementById('hist_genre').getContext('2d');
var hist_genre = new Chart(ctx_hist_genre, {
    type: 'bar',
    data: hist_genre_data,
    options: {
        responsive: true,
        legend: {
            position: 'top'
        },
        scales: {
            yAxes: [{
                ticks: {
                    min: 0
                }
            }]
        }
    }
});

var getHistGenre = function(){
    $.ajax({
        type: 'GET',
        url: url_rated_movies_statistics_hist_genre_data,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result)
            hist_genre.data.labels = json_result['data']['genre'];
            hist_genre.data.datasets[0].data = json_result['data']['nr_ratings']
            hist_genre.update();
        }
    });
}
//------------------- Average Rating per Genre -------------------------------------------

var avg_rating_per_genre_data = {
    labels: [],
    datasets: [{
        label: 'Ratings',
        backgroundColor: '#dddddd',
        borderWidth: 1,
        data: []
    }]
}

var ctx_avg_rating_per_genre = document.getElementById('bar_avg_rating_per_genre').getContext('2d');
var bar_avg_rating_per_genre = new Chart(ctx_avg_rating_per_genre, {
    type: 'bar',
    data: avg_rating_per_genre_data,
    options: {
        responsive: true,
        legend: {
            position: 'top'
        },
        scales: {
            yAxes: [{
                ticks: {
                    min: 0
                }
            }]
        }
    }
});


var getAvgRatingGenre = function(){
    $.ajax({
        type: 'GET',
        url: url_avg_ratings_genre_data,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result)
            bar_avg_rating_per_genre.data.labels = json_result['data']['genre'];
            bar_avg_rating_per_genre.data.datasets[0].data = json_result['data']['avg_rating']
            bar_avg_rating_per_genre.update();
        }
    });
}


//------------------- Number of Rating per Year -------------------------------------------

var hist_rating_year_data = {
labels: [],
    datasets: [{
        label: 'Ratings',
        backgroundColor: '#dddddd',
        borderWidth: 1,
        data: []
    }]
}

var ctx_hist_rating_year = document.getElementById('hist_rating_year').getContext('2d');
var hist_rating_year = new Chart(ctx_hist_rating_year, {
    type: 'bar',
    data: hist_rating_year_data,
    options: {
        responsive: true,
        legend: {
            position: 'top'
        },
        scales: {
            yAxes: [{
                ticks: {
                    min: 0
                }
            }]
        }
    }
});

var getRatingsPerYear = function(){

    $.ajax({
        type: 'GET',
        url: url_ratings_per_year,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result);
            hist_rating_year.data.labels = json_result['data']['year'];
            hist_rating_year.data.datasets[0].data = json_result['data']['nr_ratings'];
            hist_rating_year.update();
        }
    });
};