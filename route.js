const express = require('express');
const IPSroute = express.Router();
const WebSocket = require('ws')
const wss = new WebSocket.Server({ port: 4000 }); 

IPSroute.route('/GPS').get(function (req, res) {
    res.send('welcome to GPS')
    wss.on('connection', function connection(ws) { // สร้าง connection
        ws.on('message', function incoming(message) {

          console.log('received: %s', message);
        });
      ws.send('start');
      });
});
IPSroute.route('/').get(function (req, res) {
    res.send('welcome to APP')
});
module.exports = IPSroute;