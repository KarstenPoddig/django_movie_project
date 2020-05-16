
var getHistogram = function(){

    $.ajax({
        type: 'GET',
        url: url_analysis_histogram_data,
        dataType: 'json',
        cache: true,
        success: function(json_result){
            console.log(json_result);
            document.getElementById('histogram_result_area').innerHTML = 'Test';
        }
    })
}