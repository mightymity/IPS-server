const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8385}); 
// สร้าง websockets server ที่ port 4000
wss.on('connection', function connection(ws) { // สร้าง connection
  ws.on('message', function incoming(message) {

    var buffer1 = []
    var buffer3 = []
    var buffer4 = []
    var buffer5 = []
    //position of rasberrypi
    var positionOfR1X = 0
    var positionOfR1Y = 0
    var positionOfR3X = 0
    var positionOfR3Y = 4
    var positionOfR4X = 4
    var positionOfR4Y = 4
    var positionOfR5X = 4
    var positionOfR5Y = 0


    // รอรับ data อะไรก็ตาม ที่มาจาก client แบบตลอดเวลา
      console.log('received: %s', message);

      //test print data after change to new format
      data_withRouter = data_newformat(message)

      //extract RSSI from data_withRouter
      var onlyRSSI = data_withRouter.slice(1,data_withRouter.length)

      
      if (data_withRouter[0] == 'R1' && buffer1.length < 200){
        buffer1.push(onlyRSSI)
      }
      if (data_withRouter[0] == 'R3' && buffer1.length < 200){
        buffer3.push(onlyRSSI)
      }
      if (data_withRouter[0] == 'R4' && buffer1.length < 200){
        buffer4.push(onlyRSSI)
      }
      if (data_withRouter[0] == 'R5' && buffer1.length < 200){
        buffer5.push(onlyRSSI)
      }

      var buffers = [buffer1,buffer3,buffer4,buffer5]

      var routerCoord = [[positionOfR1X, positionOfR1Y],
                        [positionOfR3X, positionOfR3Y],
                        [positionOfR4X, positionOfR4Y],
                        [positionOfR5X, positionOfR5Y]]
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
  var a = (-2.0 * x1) + (2.0 * x2)
  var b = (-2.0 * y1) + (2.0 * y2)
  var c = math.pow(distance_from_r1, 2) - math.pow(distance_from_r2, 2) - math.pow(x1, 2) + math.pow(x2, 2) - math.pow(y1, 2) + math.pow(y2, 2)

  var d = (-2. * x2) + (2.0 * x3)
  var e = (-2. * y2) + (2.0 * y3)
  var f = math.pow(distance_from_r2, 2) - math.pow(distance_from_r3, 2) - math.pow(x2, 2) + math.pow(x3, 2) - math.pow(y2, 2) + math.pow(y3, 2)

  var x_of_tracker = ((c * e) - (f * b)) / ((e * a) - (b * d))
  var y_of_tracker = ((c * d) - (a * f)) / ((b * d) - (a * e))

  var pos = [x_of_tracker, y_of_tracker]

  return pos



}
});