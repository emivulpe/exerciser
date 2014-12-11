var currentStep = 0; // Stores the current step you're on. 0 means initial state.
var d = new Date();
var lastTime = d.getTime();
var csrftoken = getCookie('csrftoken');
var direction = "next";
var answer = "";

console.log(csrftoken);

// When we go back, we need to undo what we did. So this maps an action to its inverse (e.g. when you revert a show, you hide it).
var undoMapping = {
	'show': 'hide',
	'hide': 'show',
	'highlight' : 'unhighlight',
	'unhighlight' : 'highlight',
}


function doReset() {
	$("*[id^='fragment_']").css("background-color", "transparent");
	$("*[id^='fragment_']").hide();
	$('#explanation').html('');
	currentStep = 0;
}

function goToStep(direction) {
	direction = direction;
	$("*[id^='fragment_']").each(function() {
		if ($(this).css('background-color') == 'blue'){
			$(this).css("background-color", "transparent");
		}
	});
	if (direction == "back") {
		currentStep--;
	}
	$("*[id^='fragment_']").css("background-color", "transparent");
	var totalSteps = steps.length; // Total number of possible steps
	if (currentStep == totalSteps){
		$("#btn_next").hide();
	}
	else if(currentStep == 0 && direction == "back") {
		$("#btn_prev").hide();
	}
	else {
		$("#btn_prev").show();
		$("#btn_next").show();
		

		
		for (var i = 0; i < steps[currentStep].length; i++) {
			var currentAction = steps[currentStep][i];
			var text = currentAction[0];
			var action = currentAction[1];

				// If we want to go back, we need to reverse the action!
			if (direction == "back") {
				action = undoMapping[action];
			}
			answer = "";
			if (action == "question"){
				var options = currentAction[2];
				askQuestion(text, options);
				console.log("step " + (currentStep + 1));
			}
			else{
				doAction(text, action); // Do the action! Show, hide, and (eventually) highlight/unhighlight.
			}
		}
		if(action != "question"){
			console.log("step " + (currentStep + 1));
			var now = new Date().getTime();
			$.post("/exerciser/log_info/",
			{
			time : (now - lastTime) / 1000,
			step : currentStep + 1,
			direction : direction,
			answer : answer,
			csrfmiddlewaretoken : csrftoken
			});
			lastTime = now;
		}
		//console.log(explanations);
		var text = explanations[currentStep].substring(1, explanations[currentStep].length-1);;
		$('#explanation').html('Step '+ (currentStep + 1) + ': <br>' + text);
		
		if (direction == "next") {
			currentStep++;
		}
	}

}




function doAction(fragment, action) {
	var fragmentId = "fragment_" + fragment;
	var object = $('#' + fragmentId);
	
	if (action == "show") {
		object.show();
		object.css("background-color", "#BC8F8F");
	}
	
	else if (action == "hide") {
		object.hide();
	}
	
	else if (action == "highlight") {
		object.css("background-color", "#DA70D6");
	}
	
	else if (action == "unhighlight") {
		object.css("background-color", "transparent");
	}
}

function askQuestion(questionText, options){
	$('#question_text').text(questionText);
	$("#options").empty();
	for (var option_num = 0; option_num < options.length; option_num++){
		var option = options[option_num];
		option_elem = "<input class = 'option' id='option".concat(option_num,"' name='option' type='radio' value = \"", option, "\"/>",option,"<br>");
		$("#options").append(option_elem);
	}
	ShowDialog();
}

// Use JQuery to pick up when the user pushes the next button.
$('#btn_next').click(function() {
	goToStep("next");
});

// And again, bind an event to the previous button.
$('#btn_prev').click(function() {
	goToStep("back");
});

$('#btn_reset').click(function() {
	doReset();
});


$(document).ready(function ()
{
	$("#btnClose").click(function (e){
		HideDialog();
		e.preventDefault();
	});

	$("#btnSubmit").click(function (e){
		answer = $(".options input[type='radio']:checked").val();
		console.log($(".options input[type='radio']:checked"));
		console.log(answer);
		$("#output").html("<b>The user selected answer: </b>" + answer);
		HideDialog();
		e.preventDefault();
		var now = new Date().getTime();
		$.post("/exerciser/log_info/",
		{	time : (now - lastTime) / 1000,
			step : currentStep,
			direction : direction,
			answer : " The answer the user selected is: " + answer,
			csrfmiddlewaretoken : csrftoken
		});
		lastTime = now;
		goToStep("next");
		$( "#explanation" ).prepend( "<p>You answered: ".concat(answer).concat("</p>") );
	});

});

function ShowDialog(){
	$("#overlay").show();
	$("#dialog").fadeIn(300);
	$("#overlay").unbind("click");
}

function HideDialog(){
	$("#overlay").hide();
	$("#dialog").fadeOut(300);
} 

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
