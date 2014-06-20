var testid = ['1234'];

$("#ID_PrimeActivity").attr("autocomplete", "off");
$('#ID_PrimeActivity').typeahead({prefetch: "static/sample1.json"});

$("#ID_Meetupid").attr("autocomplete", "off");
$('#ID_Meetupid').typeahead({local: testid});


$("#ID_Interest1").attr("autocomplete", "off");
$('#ID_Interest1').typeahead({prefetch: "static/sample1.json"});
$("#ID_Interest2").attr("autocomplete", "off");
$('#ID_Interest2').typeahead({prefetch: "static/sample1.json"});
$("#ID_Interest3").attr("autocomplete", "off");
$('#ID_Interest3').typeahead({prefetch: "static/sample1.json"});

$('.tt-hint').addClass('form-control');
//$('#PID1').typeahead({local: mySource});

