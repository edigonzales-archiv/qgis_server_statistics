d3.json("daily.json", function(data) {
        
    console.log(data[0]);
    color = nv.utils.getColor();
    console.log(color);
    

    nv.addGraph(function() {
        var chart = nv.models.lineChart()
                .interpolate("monotone")  
                .margin({left: 50, right: 50})    
                .useInteractiveGuideline(true)
                .x(function(d) { return d[0] })
                .y(function(d) { return d[1] });
                
        chart.xAxis
            .axisLabel("X-axis Label");

        chart.yAxis
            .axisLabel("Y-axis Label")
            .tickFormat(d3.format("d"))
            ;
            
        chart.xAxis.tickFormat(function(d) {
            console.log(d);
            var dx = data[0].values[d] && data[0].values[d][0] || 0;
        //console.log(data[0].values[d]);
            //return d3.time.format('%H:%M')(new Date(dx))
            return d3.time.format('%d.%m %H:%M')(new Date(d));
        });            

        d3.select("svg")
            .datum(data)
            .transition().duration(500).call(chart);

        nv.utils.windowResize(
                function() {
                    chart.update();
                }
            );

        return chart;

    });
    
});
