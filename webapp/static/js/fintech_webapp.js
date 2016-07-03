function loadWithAjax(url, successHandler) {
	$.ajax(url, {
        	cache: false,
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
			chart.addListener("rendered", function(e) {
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