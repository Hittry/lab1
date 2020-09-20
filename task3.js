const mUrl = '/home/alexander/labFirst/';
var express = require('express');
var app = express();

app.get('/', function(request, response) {
  response.send("<h4> "+ mUrl + "task3?Text1=Promis1_complete&Text2=Promise2_complete&Text3=error</h4>")
})
app.get(mUrl + 'task3', function (req, res) {
const promise1 = new Promise((resolve, reject) => {
    setTimeout(() => {
        resolve('Promise1 выполнен');
    }, 2000);
});
const promise2 = new Promise((resolve, reject) => {
    setTimeout(() => {
        resolve('Promise2 выполнен');
    }, 1500);
});
let resText = req.query.Text1;
let resT = req.query.Text2;
resText += " ";
resText += resT;
let resTe = req.query.Text3;
Promise.all([promise1, promise2])
    .then((data) => res.send(resText))
    .catch((error) => res.send(resTe));
});
app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
