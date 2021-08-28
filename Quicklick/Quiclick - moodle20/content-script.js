
LOGINNER_TIMEOUT = 100;
LOGINNER_TRIES = 20;

window.onload=function() {
	console.log("Page loaded");
	clickLogin();
}

function clickLogin() {
	var foundElements = $(".btn-primary");
	/* if (foundElements.length != 1) { 
		console.log("Find elements error: " + foundElements.outerHTML);
		return;
	}*/
	var firstElement = foundElements[0];
	console.log("First element is:\n" + firstElement.outerHTML);
	if (firstElement.value != "Log in" & firstElement.value != "התחברות") {
		console.log("First element is not login button, quiting");
		return;
	}
	console.log("Login found");
	var usernameInput = $("#login_username");
	var passInput = $("#login_password");
	console.log("usernameInput.length is:" + usernameInput.length);
	console.log("usernameInput.val is:" + usernameInput.val());
	usernameInput[0].value = '20536059'
	passInput[0].value = '12584'
	var tryIn = 0;
	if (usernameInput.length != 1 || passInput.length != 1) {
		tryIn = 1000;
		console.log("Username or password input not found, will try login in " + tryIn + " ms.");
	}
	setTimeout(function() { tryClick(firstElement, usernameInput, passInput); }, tryIn);
}

function tryClick(loginBtt, userInput, passInput) {
	if (userInput != null && passInput != null) {
		if (userInput.val() == "" || passInput.val() == "") {
			LOGINNER_TRIES--;
			if (LOGINNER_TRIES == 0) {
				console.log("No autofill, giving up");
				loginBtt.click();
				return;
			}
			console.log("Autofill did not load yet, will try again in " + LOGINNER_TIMEOUT + " ms (" + LOGINNER_TRIES + " tries left)");
			setTimeout(function() { tryClick(loginBtt, userInput, passInput); }, LOGINNER_TIMEOUT);
			return;
		}
	}
	console.log("Clicking!");
	loginBtt.click();
	loginBtt.style.background = "green";
	loginBtt.style.color = "white";
}
