
var histogram_data = {
    labels: [1, 5, 7, 10, 11, 12, 15],
    datasets: [{
        label: 'Dataset 1',
        backgroundColor: '#dddddd',
        borderWidth: 1,
        data: [1,2,3,4,-1,-2,3]
    }]
};

var ctx = document.getElementById('histogram').getContext('2d');
var histogram = new Chart(ctx, {
    type: 'bar',
    data: histogram_data,
    options: {
        responsive: true,
        legend: {
            position: 'top',
        },
        scales: {
            yAxes: [{
                ticks: {
                    min: 0,
                    stepSize: 1.0
                }
            }]
        }
    }
});


var getHistogram = function(){

    $.ajax({
        type: 'GET',
        url: url_analysis_histogram_data,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result);
            histogram.data.labels = json_result['data']['nr_ratings'].slice(0,10);
            histogram.data.datasets[0].data = json_result['data']['frequency'].slice(0,10);
            histogram.update();

        }
    })
}