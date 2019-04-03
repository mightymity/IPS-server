const WebSocket = require('ws');
const numjs = require('numjs')
const Dict = require("collections/dict");
const wss = new WebSocket.Server({ port: 8385}); 
// สร้าง websockets server ที่ port 4000

//global variable
var buffer1 = []
var buffer3 = []
var buffer4 = []
var buffer5 = []
var buffers = [buffer1,buffer3,buffer4,buffer5]
wss.on('connection', async function connection(ws) { // สร้าง connection
  ws.on('message', function incoming(message) {

    
    //position of rasberrypi
    var positionOfR1X = 0
    var positionOfR1Y = 0
    var positionOfR3X = 0
    var positionOfR3Y = 4
    var positionOfR4X = 4
    var positionOfR4Y = 4
    var positionOfR5X = 4
    var positionOfR5Y = 0

    var routers = {'R1': 999, 'R3': 999, 'R4': 999, 'R5': 999}

    //static variable
    rssiRefMean = [-58.44]
    nMean = [1.811]

    // รอรับ data อะไรก็ตาม ที่มาจาก client แบบตลอดเวลา
      console.log('received: %s', message);

      //test print data after change to new format
      data_withRouter = data_newformat(message)
      console.log(data_withRouter)
  
      //extract RSSI from data_withRouter
      var onlyRSSI = data_withRouter[1]

      //น่าจะทำผิด
      //var onlyRSSI = data_withRouter.slice(1,data_withRouter.length)
      
      console.log(onlyRSSI)
      onlyRSSI = JSON.parse(onlyRSSI);
      
      if (data_withRouter[0] == 'R1' && buffer1.length < 200){
        buffer1 = buffer1.concat(onlyRSSI)
        console.log('test')
      }
      if (data_withRouter[0] == 'R3' && buffer3.length < 200){
        buffer3 = buffer3.concat(onlyRSSI)
      }
      if (data_withRouter[0] == 'R4' && buffer4.length < 200){
        buffer4 = buffer4.concat(onlyRSSI)
      }
      if (data_withRouter[0] == 'R5' && buffer5.length < 200){
        buffer5 = buffer5.concat(onlyRSSI)
      }
      buffers = [buffer1,buffer3,buffer4,buffer5]
      console.log(buffers)

      var routerCoord = [[positionOfR1X, positionOfR1Y],
                        [positionOfR3X, positionOfR3Y],
                        [positionOfR4X, positionOfR4Y],
                        [positionOfR5X, positionOfR5Y]]

      var buffer_length = [buffer1.length,buffer3.length,buffer4.length,buffer5.length]
      var count = 0
      for(var i = 0; i < buffer_length.length; ++i){
        if(buffer_length[i] == 200)
            count++;
      }
      if (count == 4){
        for (var i = 0; i < 4; i++){
            var rssiMean = numjs.mean(buffers[i])
            var distanceMean = 10 ** ((rssiMean - (rssiRefMean[0])) / (-10 * nMean[0]))
            var keys = Object.keys(routers)
            keys.forEach((key)=> {
              routers[key] = distanceMean
            } )
        }
        var pi = Object.values(routers)
        var routerUse = [0,1,2,3]

        //Trilateration

        //remove the far one 
        //var far_rasverrypi = pi.index(max(pi))
        var meanPosition = cal_position(routerCoord[routerUse[0]][0],
          routerCoord[routerUse[0]][1],
          routerCoord[routerUse[1]][0],
          routerCoord[routerUse[1]][1],
          routerCoord[routerUse[2]][0],
          routerCoord[routerUse[2]][1],
          pi[routerUse[0]],
          pi[routerUse[1]],
          pi[routerUse[2]])



      }
      console.log(meanPosition)

  });

/*
ws.on('close', function close() {
  // จะทำงานเมื่อปิด Connection ในตัวอย่างคือ ปิด Browser
    console.log('disconnected');
  });
*/


//form new_data
function data_newformat(str) {
  
  var newform = str.split(" :");
  return newform
  }
//trilateration
function cal_position(x1, y1, x2, y2, x3, y3, distance_from_r1, distance_from_r2, distance_from_r3){
  console.log('log')
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
});