var express = require('express');
var app = express();
app.get('/', function (req, res) {
	let fruits = ["Яблоко", "Апельсин", "Слива"];
	for(let i = 0; i<2;i++){
    		fruits.push(fruits[i])
	}
	console.log(fruits)
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
