

function initrequest(){
	const xhr = new XMLHttpRequest();
	xhr.open("GET", "http://127.0.0.1:5000/initscanner");
	xhr.send();

};


function Yplus(){
	const xhr = new XMLHttpRequest();
	xhr.open("GET", "http://127.0.0.1:5000/incY");
	xhr.send();

};

function Yminus(){
	const xhr = new XMLHttpRequest();
	xhr.open("GET", "http://127.0.0.1:5000/decY");
	xhr.send();

};
function PlateUp(){
	const xhr = new XMLHttpRequest();
	xhr.open("GET", "http://127.0.0.1:5000/decZ");
	xhr.send();

};
function PlateDown(){
	const xhr = new XMLHttpRequest();
	xhr.open("GET", "http://127.0.0.1:5000/incZ");
	xhr.send();

};
// Theresa's function 
function Process(){
	const xhr = new XMLHttpRequest();
	xhr.open("GET", "http://127.0.0.1:5000/processing");
	xhr.send()
};
// end of Theresa's function


function ulshow(){
	document.getElementById("im1").style.display = ""; 
 	document.getElementById("im2").style.display = "none"; 

 	document.getElementById("li2").className = ""; 
 	document.getElementById("li1").className = "is-active";
}

function feedshow(){
	document.getElementById("im2").style.display = ""; 
 	document.getElementById("im1").style.display = "none"; 
 	
 	document.getElementById("li1").className = ""; 
 	document.getElementById("li2").className = "is-active"; 
}
