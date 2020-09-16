var express = require('express');
var app = express();
app.get('/', function (req, res) {
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
Promise.all([promise1, promise2])
    .then((data) => console.log(data[0], data[1]))
    .catch((error) => console.log(error));
});
app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});
