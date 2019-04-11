const SocketServer = require('ws').Server;
const express = require('express');
const cors = require('cors');
const numjs = require('numjs');
const bodyParser = require('body-parser');
const app = express();
const IPSroute = require('./route')
const port = process.env.PORT || 8385;

//global variable
var buffer1 = []
var buffer4 = []
var buffer5 = []
var buffer7 = []
var buffers = [buffer1,buffer4,buffer5,buffer7]
var routers = {'R1': 999, 'R4': 999, 'R5': 999, 'R7': 999}
var count = 0

app.use(cors());
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());
app.use('/',IPSroute)


var server = app.listen(port, function () {
    console.log('node.js static server listening on port: ' + port + ", with websockets listener")
})




const wss = new SocketServer({ server });
//init Websocket ws and handle incoming connect requests
wss.on('connection', function connection(ws) {
    console.log("connection ...");
    //on connect message
    ws.on('message', function incoming(message) {
        console.log('received: %s', message);

        //position of rasberrypi
    var positionOfR1X = 0
    var positionOfR1Y = 0
    var positionOfR3X = 0
    var positionOfR3Y = 4
    var positionOfR4X = 4
    var positionOfR4Y = 4
    var positionOfR5X = 4
    var positionOfR5Y = 0


    //static variable
    rssiRefMean = [-58.44]
    nMean = [1.811]
    
    

      //test print data after change to new format
      data_withRouter = data_newformat(message)
      ///console.log(data_withRouter)
  
      //extract RSSI from data_withRouter
      var onlyRSSI = data_withRouter[1]

      //น่าจะทำผิด
      //var onlyRSSI = data_withRouter.slice(1,data_withRouter.length)
      
      ///console.log(onlyRSSI)
      onlyRSSI = JSON.parse(onlyRSSI);
      
      if (data_withRouter[0] == 'R1' && buffer1.length < 20){
        buffer1 = buffer1.concat(onlyRSSI)
      }
      if (data_withRouter[0] == 'R4' && buffer4.length < 20){
        buffer4 = buffer4.concat(onlyRSSI)
      }
      if (data_withRouter[0] == 'R5' && buffer5.length < 20){
        buffer5 = buffer5.concat(onlyRSSI)
      }
      if (data_withRouter[0] == 'R7' && buffer7.length < 20){
        buffer7 = buffer7.concat(onlyRSSI)
      }
      buffers = [buffer1,buffer4,buffer5,buffer7]
      ///console.log(buffers)

      var routerCoord = [[positionOfR1X, positionOfR1Y],
                        [positionOfR3X, positionOfR3Y],
                        [positionOfR4X, positionOfR4Y],
                        [positionOfR5X, positionOfR5Y]]

      var buffer_length = [buffer1.length,buffer4.length,buffer5.length,buffer7.length]
      var count = 0
      for(var i = 0; i < buffer_length.length; ++i){
        if(buffer_length[i] == 20)
            count++;
      }
      if (count == 4){
        for (var i = 0; i < 4; i++){
            var rssiMean = numjs.mean(buffers[i])
            var distanceMean = 10 ** ((rssiMean - (rssiRefMean[0])) / (-10 * nMean[0]))
            if (i == 0) routers.R1 = distanceMean
            if (i == 1) routers.R4 = distanceMean
            if (i == 2) routers.R5 = distanceMean
            if (i == 3) routers.R7 = distanceMean
        }
        var pi = Object.values(routers)
        ///console.log(pi)
        var routerUse = [0,1,2,3]

        //Trilateration

        //remove the far one 
        //var far_rasverrypi = pi.index(max(pi))
        ///console.log(routers)
        var meanPosition = cal_position(routerCoord[routerUse[0]][0], //call function cal_position
        routerCoord[routerUse[0]][1],
        routerCoord[routerUse[1]][0],
        routerCoord[routerUse[1]][1],
        routerCoord[routerUse[2]][0],
        routerCoord[routerUse[2]][1],
        pi[routerUse[0]], //distance from R1
        pi[routerUse[1]], //distance from R4
        pi[routerUse[2]]) //distance from R5
        console.log(meanPosition)

        //clear variable
        buffer1 = []
        buffer4 = []
        buffer5 = []
        buffer7 = []
        buffers = [buffer1,buffer4,buffer5,buffer7]
        routers = {'R1': 999, 'R4': 999, 'R5': 999, 'R7': 999}
        count = 0


      }
      
    });

    function data_newformat(str) {
  
        var newform = str.split(" :");
        return newform
        }
      //trilateration
      function cal_position(x1, y1, x2, y2, x3, y3, distance_from_r1, distance_from_r2, distance_from_r3){
        var a = (-2.0 * x1) + (2.0 * x2)
        var b = (-2.0 * y1) + (2.0 * y2)
        var c = Math.pow(distance_from_r1, 2) - Math.pow(distance_from_r2, 2) - Math.pow(x1, 2) + Math.pow(x2, 2) - Math.pow(y1, 2) + Math.pow(y2, 2)
      
        var d = (-2. * x2) + (2.0 * x3)
        var e = (-2. * y2) + (2.0 * y3)
        var f = Math.pow(distance_from_r2, 2) - Math.pow(distance_from_r3, 2) - Math.pow(x2, 2) + Math.pow(x3, 2) - Math.pow(y2, 2) + Math.pow(y3, 2)
      
        var x_of_tracker = ((c * e) - (f * b)) / ((e * a) - (b * d))
        var y_of_tracker = ((c * d) - (a * f)) / ((b * d) - (a * e))
      
        var pos = [x_of_tracker, y_of_tracker]
        return pos
      
      }

    ws.send('message from IPS server at: ' + new Date());
});