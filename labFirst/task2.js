var express = require('express');
var app = express();
app.get('/', function (req, res) {
function showMinutes() {
    let dNow = new Date(2020,0,1,0,0,0,0);
    let today = new Date();
    today.setHours(12,50,3,2)

    console.log("Hours difference:",dNow.getHours()- today.getHours());
    console.log("Month difference:",dNow.getMonth()- today.getMonth());
    console.log("Second difference:",dNow.getSeconds()- today.getSeconds()) ;
}
showMinutes();
});
app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
