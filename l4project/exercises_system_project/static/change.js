var currentStep = 0; // Stores the current step you're on. 0 means initial state.
var d = new Date();
var lastTime = d.getTime();
var csrftoken = getCookie('csrftoken');
var direction = "next";
var answer = "";
var options = "";
var lastAction = "";
var answers = {};
var wasQuestion = false;
var action;
var explanation_dict={}
var question ="";

//console.log(csrftoken);
$("#btn_prev").hide();


function goToStep(direction) {
	console.log(Object.keys(answers).length);
	direction = direction;

	if (direction == "back") {
		currentStep--;
	}
	$("*[id^='fragment_']").css("background-color", "transparent");
	$('#explanation').html("");

	var totalSteps = steps.length; // Total number of possible steps
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
			action = currentAction[1];
			if(action == "question"){
				wasQuestion = true;
			}
				// If we want to go back, we need to reverse the action!
			if (direction == "back") {
				action = undoMapping[action];
			}
			
			if (action == "question"){
				if(direction == "next" && answers[currentStep.toString()] == undefined){
					//console.log(currentStep.toString().concat(answers[currentStep.toString()]));
					console.log(currentStep);
					question = text;
					options = currentAction[2];
					askQuestion(text, options);
					//console.log(answers[currentStep]);

					//console.log("step " + (currentStep + 1));
				}
			}
			else{
				doAction(text, action); // Do the action! Show, hide, and (eventually) highlight/unhighlight.
			}
			
		}
		if(action != "question"){
			//console.log("step " + (currentStep + 1));
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
		console.log(action);
		console.log(direction);
		
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
			console.log(explanationText);
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
	wasQuestion = false;
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
	var explanationText ="." + questionText;
	for (var option_num = 0; option_num < options.length; option_num++){
		var option = options[option_num];
		option_elem = "<input class = 'option' id='option".concat(option_num,"' name='option' type='radio' value = \"", option, "\"/>",option,"<br>");
		$("#options").append(option_elem);
		explanationText += option;
	}
	explanationText += ".";
	ShowDialog();
}

// Use JQuery to pick up when the user pushes the next button.
$('#btn_next').click(function() {
	wasQuestion = false;
	//console.log(wasQuestion);
	goToStep("next");
	//console.log(wasQuestion);
});

// And again, bind an event to the previous button.
$('#btn_prev').click(function() {
	wasQuestion = false;
	//console.log(wasQuestion);
	goToStep("back");
	//console.log(wasQuestion);
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
		//console.log(currentStep.concat(answers[currentStep]));
		answers[currentStep-1] = answer;
		console.log(answers[currentStep.toString()]);
		console.log(answers);
		//console.log("dict works ".concat(answers));
		//console.log($(".options input[type='radio']:checked"));
		//console.log(answer);
		explanation_dict[currentStep-1] = " You answered: " + answer + "<br>" + explanation_dict[currentStep-1];
		//$("#output").html("<b>The user selected answer: </b>" + answer);
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
		action = ""; //reset action
		answer = " You answered: " + answer + "<br>";
		goToStep("next");
		//$( "#explanation" ).prepend( "<p>You answered: ".concat(answer).concat("</p>") );
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
