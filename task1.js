const mUrl = '/home/alexander/labFirst/';
var express = require('express');
var app = express();

app.get('/', function(request, response) {
  response.send("<h4> "+ mUrl + "task1?fruit=Apple&fruit=Orange&fruit=bannana</h4>")
})

app.get(mUrl + "task1", function (req, res) {
	console.log(req.query)
	let fruits = req.query.fruit;
	let responseText = '<ul>';
	for(let i = 0; i<2;i++){
    		fruits.push(fruits[i]);
	}
	for (let j = 0; j < fruits.length; j++) {
    responseText += '<li>' + fruits[j] + '</li>';
  }
	responseText += '</ul>';
 	res.send(responseText);
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
