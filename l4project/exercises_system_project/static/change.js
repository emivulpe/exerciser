var currentStep = 0; // Stores the current step you're on. 0 means initial state.
var d = new Date();
var lastTime = d.getTime();
var csrftoken = getCookie('csrftoken');
var direction = "next";
var answer = "";
var explanation_dict={}

$("#btn_prev").hide();


function goToStep(direction) {

	var totalSteps = steps.length; // Total number of possible steps
	$("*[id^='fragment_']").css("background-color", "transparent");
	$('#explanation').html("");
	direction = direction;

	if (direction == "back") {
		currentStep--;
	}


	if (currentStep == totalSteps-1 && direction == "next"){
		$("#btn_next").hide();
	}
	else if(currentStep == 0 && direction == "back") {
		$("#btn_prev").hide();
	}
	else {
		$("#btn_prev").show();
		$("#btn_next").show();
	}

	if(currentStep >= 0 && currentStep < totalSteps){	
		for (var i = 0; i < steps[currentStep].length; i++) {
			var currentAction = steps[currentStep][i];
			var text = currentAction[0];
			var action = currentAction[1];
			// If we want to go back, we need to reverse the action!
			if (direction == "back") {
				action = undoMapping[action];
			}
			
			if (action == "question"){
				if(direction == "next" && explanation_dict[currentStep] == undefined){
					var options = currentAction[2];
					askQuestion(text, options);
				}
			}
			else{
				doAction(text, action); // Do the action! Show, hide, and (eventually) highlight/unhighlight.
			}
			
		}
		if(action != "question"){
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

		
		if (direction == "next" && explanation_dict[currentStep] == undefined) {
		
			var explanationText= answer +'Step '+ (currentStep + 1) +"/" + totalSteps + ': <br>';
			if(action!="question"){
				explanationText +=  explanations[currentStep].substring(1, explanations[currentStep].length-1);
				answer = "";
			}
			else {
				explanationText += text;
				for (var option_num = 0; option_num < options.length; option_num++){
					explanationText += "<br>" + options[option_num];
				}
			}
			$('#explanation').html(explanationText);
			explanation_dict[currentStep] = explanationText;
			currentStep++;

		}
		else if (direction == "next" && explanation_dict[currentStep] != undefined){
			$('#explanation').html(explanation_dict[currentStep]);
			currentStep++;

		}
		else {
			$('#explanation').html(explanation_dict[currentStep-1]);
		}
	}

}


// When we go back, we need to undo what we did. So this maps an action to its inverse (e.g. when you revert a show, you hide it).
var undoMapping = {
	'show': 'hide',
	'hide': 'show',
	'highlight' : 'unhighlight',
	'unhighlight' : 'highlight',
	'question' : 'question',
}


function doReset() {
	$("*[id^='fragment_']").css("background-color", "transparent");
	$("*[id^='fragment_']").hide();
	$('#explanation').html('');
	$("#btn_prev").hide();
	currentStep = 0;
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
		explanation_dict[currentStep-1] = " You answered: " + answer + "<br>" + explanation_dict[currentStep-1];
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
		answer = " You answered: " + answer + "<br>";
		goToStep("next");
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
