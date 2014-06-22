var thecurrentdata;
var currentmatch_ind = 0;
var totalmatches = 0;
//tabulate_new('');

$(function() {
	$('#ID_getmatch').bind('click', function() {
		console.log("get match clicked")

		$.getJSON('/generate_match', {
			primeint: $('input[id="ID_PrimeActivity"]').val(),
			int1: $('input[id="ID_Interest1"]').val(),
			int2: $('input[id="ID_Interest2"]').val(),
			int3: $('input[id="ID_Interest3"]').val(),
			}, function(data) {
			thecurrentdata = data;
			currentmatch_ind = 0;
			//console.log(data)
			//$("#result").text(data.result);

			
			// render the table
			totalmatches = Object.keys(data).length
			tabulate_new(data[0]);
		});
		return false;
	});
});

function tabulate_new(thedata) {
	//
	var testdata = thedata['scores'];
	var thelabels = thedata['catagories'];
	var matchsets = thedata['matchset_rest'];

	d3.selectAll("#newpanel").remove();

	console.log(thedata)
	var datadiv = d3.select('#datapanel');
	var datapanel = datadiv.append("div").attr("id","newpanel").attr("class","panel panel-default")
				.append("div").attr("class","panel-body")
	
	var row_top = datapanel.append("div").attr("class","row").style("padding-bottom","25px").attr("align","center");
	row_top.append("h1").append("span").attr("class","label label-danger").append("a").attr("href",thedata['link']).text(thedata['name']);


	var row_mid = datapanel.append("div").attr("class","row").attr("align","center");
	var col_left = row_mid.append("div").attr("class","col-md-4");
	var col_right = row_mid.append("div").attr("class","col-md-8").attr("align","left");

	var row_bot = datapanel.append("div").attr("class","row").style("padding-left","20px").style("padding-right","20px").attr("align","center");

	var row_for_button = datapanel.append("div").attr("class","row").attr("align","right").style("padding-right","10px");
	//var row_bot_left = row_bot.append("div").attr("class","col-md-4").style("padding-top","35px");
	//var row_bot_right = row_bot.append("div").attr("class","col-md-8");



	var col_left1 = col_left.append("div").attr("class","row");
	var col_left2 = col_left.append("div").attr("class","row")
			.append("img")
			.attr("width",150)
			.attr("height",150)
			.attr("class","roundrect")
			.attr("src", thedata['photo']);

	var col_left3 = col_left.append("div").attr("class","row")
	col_left3.append("h3").text(thedata['location']);

	nextbt = row_for_button
		.append("button")
		.attr("id","nextbt")
		.attr("align","left")
		.attr("class","btn btn-lg")
		.text("Next Match!");
	$('#nextbt').bind('click', function() { 
		currentmatch_ind = currentmatch_ind +1;
		tabulate_new(thecurrentdata[currentmatch_ind%totalmatches]);
	});

	//create svg plot
	var barHeight = 45;

	var margin = {top: 0, right: 30, bottom: 0, left: 10},
    			width = 430 - margin.left - margin.right,
    			height = 180 - margin.top - margin.bottom;
		

	

	var svg = col_right.append("svg")
		.attr("class","chart")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


	var x = d3.scale.linear()
	    .domain([0, d3.max(testdata)])
	    .range([0, width - 150]);

	var bar = svg.selectAll("g")
	    .data(testdata)
	  .enter().append("g")
	    .attr("transform", function(d, i) { return "translate(0," + i * barHeight + ")"; })
	     
	
	var panel_interests;

	var GenerateIntPanel = function(d,i) {
		//console.log(i);
		

		if(panel_interests !== undefined) 
			panel_interests.remove();

		panel_interests = row_bot.append("div").style("padding-left","20px").attr("class","panel panel-primary").attr("align","left");
		panel_interests.append("div").attr("class","row").append("h4").text("Interests");
		var thelist = panel_interests.append("div").append("ul").attr("class","nav nav-pills");
		for(j=0; j<thedata['matchset_rest'][i].length; j++ ) {
			thelist.append("li").append("a").text(thedata['matchset_rest'][i][j])
		}
		panel_interests.append("div").attr("class","row").append("h4").text("Groups")
		var thelist = panel_interests.append("div").append("ul").attr("class","nav nav-pills");
		for(j=0; j<thedata['groupname'][i].length; j++ ) {
			thelist.append("li").append("a").text(thedata['groupname'][i][j])
		}
	}

	var RemoveIntPanel = function() {

		
	}


	bar.append("rect").attr("id","thebar").attr("class","bar")
		.on("click", GenerateIntPanel)
		.attr("width", 0)
	    	.attr("height", barHeight - 1)

		//.on("mouseout",RemoveIntPanel);
	d3.selectAll("#thebar").transition().duration(500).attr("width", x)
		
	bar.append("text")
		.attr("x", function(d) { return x(d) + 3 ; })
		.attr("y", barHeight / 2)
		.attr("dy", ".35em")
		.text(function(d,i) { return thelabels[i]; });

	


    return;
}
