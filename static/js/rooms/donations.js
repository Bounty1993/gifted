let chart = document.getElementById('chart')
let ajax = get_fetch(chart.dataset.url).then(resp => resp.json())
ajax.then(response => {
    console.log(response.data)
    Highcharts.chart("chart", response);
})