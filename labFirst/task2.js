const mUrl = '/home/alexander/labFirst/';
var express = require('express');
var app = express();

app.get('/', function(request, response) {
  response.send("<h4> "+ mUrl + "task2?Month1=3&Second1=40&Hours1=13&Minute1=15&Month2=5&Second2=50&Hours2=15&Minute2=41</h4>")
})

app.get(mUrl + 'task2', function (req, res) {
function showMinutes() {
    let m1 = req.query.Month1;
    let m2 = req.query.Month2;
    let S1 = req.query.Second1;
    let S2 = req.query.Second2;
    let H1 =req.query.Hours1;
    let H2 = req.query.Hours2;
    let Min1 = req.query.Minute1;
    let Min2 = req.query.Minute2;
    console.log(req.query)
    let responseText = "Month difference: ";
    responseText += m2-m1;
     responseText += " Hours difference: ";
      responseText += H2-H1;
      responseText += " Minutes difference: ";
      responseText += Min2-Min1;
      responseText += " Second difference: ";
      responseText += S2-S1;
    res.status(200).send((responseText).toString());
  
}
showMinutes();
});
app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
