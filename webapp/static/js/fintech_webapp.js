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
                    "captionFontSize": "28",
                    "subcaptionFontSize": "20",
                    "subcaptionFontBold": "0",
                    "subCaptionFont": "sans-serif",

                    "xAxisName":valueFieldName,
                    "xAxisNameFontSize" :"18",
                    "yAxisName": categoryFieldName,
                    "yAxisNameFontSize" :"18",

                    "paletteColors": "#ff704d",

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

                    "plotGradientColor":"#FFFF00",
                    "usePlotGradientColor": "1",

                    "trendValueBorderColor": "#123456",
                    "trendValueBorderDashGap": "3",
                    "trendValueFontBold": "1",
                    "trendValueFontSize":"12",
                    "trendValueBgColor":"#ffa31a",
                    "trendValueBorderPadding":"5",
                    "trendValueBgColor":"#ffa31a",

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
                                "color": "#ff4000",
                                "valueOnTop": "1",
                                "displayvalue": "Average",
                                "thickness": "4"
                            }
                        ]
                    }
                ],
                "events": {
                    // Attach to beforeInitialize
                    "initialized": function () {
                        console.log("Initialized mychart... event called");
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
