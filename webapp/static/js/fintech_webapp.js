function loadWithAjax(url, successHandler, method, data, contentType) {
    $.ajax(url, {
        cache: false,
        method: method || 'GET',
        data: data,
        contentType: contentType || this.contentType,
        success: function (data, status, xhrObj) {
            //console.log("ajax success, data received.", data);

            successHandler(data, status, xhrObj);
        },
        error: function (xhrObj, status, errorThrown) {
            console.log(errorThrown);
        }
    });
}

function buildAmBarChart(chart, categoryFieldName, valueFieldName, barClickHandler) {
    //AmCharts.ready(function () {
    // SERIAL CHART
    //chart = new AmCharts.AmSerialChart();
    chart.categoryField = categoryFieldName;
    chart.startDuration = 1;
    chart.plotAreaBorderColor = "#DADADA";
    chart.plotAreaBorderAlpha = 1;
    chart.addClassNames = true;
    /*chart.titles = [{
     "text": "Number of times " + $('#stock_entity option:selected').text()
     + " was " + direction + " " + percent + "% from " + from_yr + " to " + to_yr
     }],*/
    // this single line makes the chart a bar chart
    chart.rotate = true;
    chart.addListener("rendered", function (e) {
        var curtain = document.getElementById("curtain");
        curtain.parentElement.removeChild(curtain);
    });

    // Category AXIS
    var categoryAxis = chart.categoryAxis;
    categoryAxis.gridPosition = "start";
    categoryAxis.gridAlpha = 0.1;
    categoryAxis.axisAlpha = 0;
    categoryAxis.title = "Companies";

    // Value AXIS
    var valueAxis = new AmCharts.ValueAxis();
    valueAxis.axisAlpha = 0;
    valueAxis.gridAlpha = 0.1;
    valueAxis.title = "Count";
    valueAxis.labelFunction = function (value, valueText, valueAxis) {
        return (value);
    };
    valueAxis.guides = [{
        value: 50,
        lineColor: "#CC0000",
        lineAlpha: 1,
        lineThickness: 1.5,
        dashLength: 5,
        inside: true,
        labelRotation: 90,
        label: "Average",
        boldLabel: true,
        //inside: false,
        position: "bottom",
        above: true,
        "balloonText": "<span style='font-size:14px; color:#000000;'><b>Average</b></span>",
    }];
    //valueAxis.position = "top";
    chart.addValueAxis(valueAxis);

    // GRAPHS
    // first graph
    var graph1 = new AmCharts.AmGraph();
    graph1.type = "column";
    graph1.title = "Count";
    graph1.valueField = valueFieldName;
    graph1.labelText = "[[value]]"
    //graph1.balloonText = "Count:[[value]]<br/>Click to Drilldown";
    graph1.lineAlpha = 0;
    //graph1.fillColors = "#ADD981";
    graph1.fillAlphas = 1;
    graph1.classNameField = "catAxisLabelCSS";
    graph1.addListener("clickGraphItem", barClickHandler /*function (event) {
     window.location = "q1_individual_entity.html";
     }*/);
    chart.addGraph(graph1);

    // LEGEND
    /*var legend = new AmCharts.AmLegend();
     chart.addLegend(legend);*/

    chart.creditsPosition = "top-right";
    //});
}


function buildFusionChart(categoryFieldName, valueFieldName,get_chart_properties,barClickHandler) {
    var chart_properties={
                    "theme": "fint",

                    "caption": get_chart_properties.titles[0].maintext,
                    "subCaption": get_chart_properties.titles[0].subtext,
                    "captionFontSize": "26",
                    "subcaptionFontSize": "20",
                    "captionFontBold": "1",
                    "subCaptionFont": "SF-UI-Text-Bold",
                    "captionFont": "SF-UI-Text-Bold",
                    "subcaptionFontSize": "26",

                    "xAxisName":valueFieldName,
                    "xAxisNameFontSize" :"16",
                    "xAxisNameFont" :"SF-Compact-Text-Bold",
                    "xAxisNameFontBold" :"1",
                    "yAxisName": categoryFieldName,
                    "yAxisNameFontSize" :"16",
                    "yAxisNameFont" :"SF-Compact-Text-Bold",
                    "yAxisNameFontBold" :"1",

                    "paletteColors": "#ff6600",

                    "placeValuesInside": "0",
                    "valueFontColor": "#000000",

                    "showAxisLines": "0",
                    "axisLineAlpha": "0",
                    "divLineAlpha": "20",
                    "alignCaptionWithCanvas": "1",
                    "showAlternateVGridColor": "0",

                    "toolTipColor": "#ffffff",
                    "toolTipBorderThickness": "0",
                    "toolTipBgColor": "#000000",
                    "toolTipBgAlpha": "80",
                    "toolTipBorderRadius": "2",
                    "toolTipPadding": "5",

                    "plotGradientColor":"#e9af03",
                    "usePlotGradientColor": "1",


                    "trendValueFontBold": "1",
                    "trendValueFontSize":"12",
                    "trendValueFontColor":"#ffffff",
                    "trendValueBorderPadding":"3",
                   // "trendValueBgColor":"#e03333",

                    "labelFontSize":"12",
                    "labelFontBold":"1",
                    "labelFont":"sans-serif"

                };
        var data = get_chart_properties.data;
        var chart_data= [];
        for (var i=0; i < data.length; i++)
        {

            chart_data.push({
            label: data[i].short_name_en,
            value: data[i].frequency,
            id: data[i].seid
            });
        }

        var DrawChart = new FusionCharts({
            type: 'bar2d',
            renderAt: 'chartdiv',
            width: '100%',
            height: '500',
            dataFormat: 'json',
            dataSource: {
                "chart": chart_properties,
                "data":chart_data ,
                "trendlines": [
                    {
                        "line": [
                            {
                                "startvalue": get_chart_properties.average,
                                "color": "#e03333",
                                "displayvalue": "Average",
                                "thickness": "2",
                                "valueOnTop":"1"
                            }
                        ]
                    }
                ],
                "events": {
                    // Attach to beforeInitialize
                    "initialized": function () {
                        //console.log("Initialized mychart... event called");
                    }
                }

            }
        });


        var myEventListener = function (eventObj, eventArgs) {
            var id;
            for (var i=0; i < chart_data.length; i++)
            {
               if(chart_data[i].label ==  eventArgs.categoryLabel  && chart_data[i].value == eventArgs.value) {
                    id = chart_data[i].id;
                    console.log('id is'+id);
                    return barClickHandler(id);
                }
            }
        };

        DrawChart.addEventListener("dataPlotClick", myEventListener);
        DrawChart.render();


}

//D3 Graph
function buildd3Chart(categoryFieldName, valueFieldName,get_chart_properties,barClickHandler){
        var data = get_chart_properties.data;
        var chart_data= [];
        for (var i=0; i < data.length; i++)
        {

            chart_data.push({
            Value: data[i].short_name_en,
            Key: data[i].frequency,
            id: data[i].seid
            });
        }

        var barConfig = {
            barGraphContainerDiv: "chartdiv",
            height:300,
            width: $("#chartdiv").width(),
            margin : {
                top: 60,
                bottom: 80,
                left: 80,
                right: 50
            },
            dataset:chart_data,  //Data Contain Key and Value Format, For Example Value = 2013 & Key = 15, Value = 2014 & Key = 25
            barGraphTitleText:get_chart_properties.titles[0].maintext,
            barGraphSubTitleText:get_chart_properties.titles[0].subtext,
            barCssClass: "bar",
            barTitleClass:"graphtitletext",
            barTextCssClass: "bartext",
            xAxisTitleCss:"xAxisTitle",
            xScaleClickable:false,
            yScaleClickable:false,
            showGraphHorizontally: true,
            showAverageLine: true,
            averageLineDataProvider:function(){  return  get_chart_properties.average }, //will run only when showAverageLine property is true.
            showScale:true, //hide X-axis Scale or if Vertical then Y-Axis Scale
            onBarClick:function(d) {
                return barClickHandler(d.id);
            }
        }
         $( "#chartdiv" ).empty();
         drawBarChart(barConfig);
}

function drawBarChart(config){

        var dataset = config.dataset;
        var w = config.width;
        var h = config.height ;
        var padding = config.padding;
        var margin = config.margin;
        var xScale,yScale,xAxis,yAxis,barwidth;

        //Create SVG element
        var svg = d3.select("#"+config.barGraphContainerDiv+"")
                    .append("svg")
                    .attr("width", w)
                    .attr("height", h + margin.top *3 )
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var g = svg.append("g")
                   .attr("transform", "translate(" + margin.left + "," + (margin.top+ (margin.top /2))+ ")");

        g.append("defs").append("clipPath")
                    .attr("id", "clip")
                    .append("rect")
                    .attr("width", w)
                    .attr("height", h );

        g.append("g")
         .attr("class", "scatter")
         .attr("clip-path", "url(#clip)");

        var g_graph = svg.select("g.scatter");

        var g_bars = g_graph.append("g");

        //Common attributes for Drawing Bar in both Horizontal & Vertical BarGraph
        var drawbar  = g_bars.selectAll("rect")
                         .data(dataset)
                         .enter()
                         .append("rect")
                         .attr("class", config.barCssClass)
                         .on('click', config.onBarClick);


		//Common Attributes for Displaying  text(bar value Above each bar) in both Horizontal & Vertical BarGraph
        var bartext= g_bars.selectAll("gs.rect")
                    .data(dataset)
                    .enter().append("text")
                    .attr("class",config.bartextcssclass);


        //Apply gradient on Bars.

	        //Append a defs (for definition) element to your SVG
			var defs = g_bars.append("defs");

			//Append a linearGradient element to the defs and give it a unique id
			var linearGradient = defs.append("linearGradient")
			    .attr("id", "linear-gradient");

			//Horizontal gradient
			linearGradient
			    .attr("x1", "0%")
			    .attr("y1", "0%")
			    .attr("x2", "100%")
			    .attr("y2", "0%");

			//Set the color for the start (0%)
			linearGradient.append("stop")
			    .attr("offset", "0%")
			    .attr("stop-color", "#e9af03");

			//Set the color for the end (100%)
			linearGradient.append("stop")
			    .attr("offset", "100%")
			    .attr("stop-color", "#ff6600");

        //BarGraph Title
            svg.append("text")
                .attr("x", w/ 2)
                .attr("y", margin.top/2)
                .attr("class",config.barTitleClass)
                .append('svg:tspan')
                .attr('x', w/ 2)
                .attr('dy', 0)
                .text(""+config.barGraphTitleText+"")
                .append('svg:tspan')
                .attr('x', w/ 2)
                .attr('dy', margin.top/2)
                .text(""+config.barGraphSubTitleText+"");


        //if showGraphHorizontally property is true then display Graph Horizontally
        if(config.showGraphHorizontally)
        {
            xScale = d3.scale.linear()
                                 .domain([0, d3.max( dataset, function(d) { return d.Key; } )  ])
                                 .range([margin.left, w - margin.left - margin.right ]);

            yScale = d3.scale.ordinal()
                                 .rangeRoundBands([0, h], .1)
                                 .domain( dataset.map(function (d) { return d.Value; }) );

            xAxis  = d3.svg.axis()
                              .scale(xScale)
                              .orient("bottom");

            yAxis  = d3.svg.axis()
                              .scale(yScale)
                              .orient("left");

            barwidth = yScale.rangeBand();

            //Specific attributes for Displaying text(bar value above each bar) in Horizontal Bargraph.
            bartext.attr("x", function (d) { return xScale(d.Key)+4; })
                   .attr("y", function (d) { return yScale(d.Value) +(barwidth/1.5); })
                   .text(function (d) { return d.Key; });

            //Specific attributes for Drawing Bar Horizontally
            drawbar.attr("x", margin.left )
                   .attr("width",function (d) { return  xScale(d.Key) - margin.left; })
                   .attr("y", function (d) { return yScale(d.Value) })
                   .attr("height",  yScale.rangeBand());

        	svg.append("text")
        		.attr("class",config.xAxisTitleCss)
	            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
	            .attr("transform", "translate("+ (w/2) +","+ ( h + margin.top *2.5 ) +")")  // centre below axis
	            .text("Number of Days");


            //Specific attributes for Drawing x-Scale in Horizontal Format
            //will run only when showScale property is true.
            if (config.showScale)
            {
               var xAxisProp = g.append("g")
                                  .attr("class", "x axis")
                                  .call(xAxis)
                                  .attr("transform", "translate(" + 0 + "," + h + ")");
                  if(config.xScaleClickable){
                    xAxisProp.on("click", function (d) { alert('clicked!'); });
                  }
            }

            //Specific attributes for Drawing y-Scale in Horizontal Format
                var yAxisProp = g.append("g")
                                  .attr("class", "y axis")
                                  .call(yAxis)
                                  .attr("transform", "translate(" + margin.left + "," + 0+ ")");
                  if(config.yScaleClickable){
                    yAxisProp.on("click", function (d) { alert('clicked!'); });
                  }

            //Vertical Average Line
            if(config.showAverageLine)
            {
            //Will Display Avg line
                 var g_avg = svg.append("g")
                 				.attr("transform", "translate("+margin.left +","+ (margin.top +5) +")")

		        	g_avg.append("line")
		        	   .attr("x1",function (d) { return xScale(config.averageLineDataProvider()); })
		        	   .attr("y1",0)
		        	   .attr("x2",function (d) { return xScale(config.averageLineDataProvider()); })
		        	   .attr("y2",h +margin.top/2)
		        	   .attr("class","line");

		        	g_avg.append("rect")
		        		 .attr("x",function (d) { return ($(".line").attr("x1") - 45); } )
		                   .attr("width",90)
		                   .attr("y", 0)
		                   .attr("height",30)
		                   .attr("class","avgtxtbox");

		            g_avg.append("text")
			              .attr("x", function (d) { return ($(".line").attr("x1")-25 );; })
			              .attr("y", 18)
			              .attr("class","avgtxt")
			              .text("Average");

			        g_avg.append("circle")
			           .attr("cx", function (d) { return xScale(config.averageLineDataProvider()); })
                       .attr("cy",25)
                       .attr("r", 7)
                       .style("fill"," #e03333");


            }
        }

    }