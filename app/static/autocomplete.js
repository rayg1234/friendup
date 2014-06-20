var testid = ['1234'];
var dictpath = "static/reduced_vocab.json";

$("#ID_PrimeActivity").attr("autocomplete", "off");
$('#ID_PrimeActivity').typeahead({prefetch: dictpath});

$("#ID_Meetupid").attr("autocomplete", "off");
$('#ID_Meetupid').typeahead({local: testid});


$("#ID_Interest1").attr("autocomplete", "off");
$('#ID_Interest1').typeahead({prefetch: dictpath});
$("#ID_Interest2").attr("autocomplete", "off");
$('#ID_Interest2').typeahead({prefetch: dictpath});
$("#ID_Interest3").attr("autocomplete", "off");
$('#ID_Interest3').typeahead({prefetch: dictpath});

$('.tt-hint').addClass('form-control');
//$('#PID1').typeahead({local: mySource});

