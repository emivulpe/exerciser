var currentStep = 0; // Stores the current step you're on. 0 means initial state.

// When we go back, we need to undo what we did. So this maps an action to its inverse (e.g. when you revert a show, you hide it).
var undoMapping = {
	'show': 'hide',
	'hide': 'show',
	'highlight' : 'unhighlight',
	'unhighlight' : 'highlight',
}

function goToStep(direction) {
	var totalSteps = steps.length; // Total number of possible steps
	
	if ((currentStep == totalSteps && direction == "next") || (currentStep == 0 && direction == "back")) {
		alert("We have reached the end or the start!");
	}
	else {
		
		if (direction == "back") {
			currentStep--;
		}
		
		for (var i = 0; i < steps[currentStep].length; i++) {
			var currentAction = steps[currentStep][i];
			var fragment = currentAction[0];
			var action = currentAction[1];
			
			doAction(fragment, action, direction); // Do the action! Show, hide, and (eventually) highlight/unhighlight.
		}
		
		if (direction == "next") {
			currentStep++;
		}
	}
}

function doAction(fragment, action, direction) {
	var object = $('#' + fragment);
	
	// If we want to go back, we need to reverse the action!
	if (direction == "back") {
		action = undoMapping[action];
	}
	
	console.log("WHAAAA");
	
	if (action == "show") {
		object.show();
	}
	else if (action == "hide") {
		object.hide();
	}
	else if (action == "highlight") {
		console.log("HEYYY");
		object.css("background-color", "yellow");
	}
	else if (action == "unhighlight") {
		object.css("background-color", "transparent");
	}
}

// Use JQuery to pick up when the user pushes the next button.
$('#btn_next').click(function() {
	goToStep("next");
});

// And again, bind an event to the previous button.
$('#btn_prev').click(function() {
	goToStep("back");
});