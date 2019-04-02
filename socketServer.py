import numpy
import asyncio
import websockets
import ast
import math
from sklearn.cluster import KMeans
from sklearn import metrics


class Server:

    def __init__(self):
        
        self.meanPosition = []
        self.nearestRouter = ''
        self.buffer1 = []
        self.buffer3 = []
        self.buffer4 = []
        self.buffer5 = []
        self.routers = {'R1': 999, 'R3': 999, 'R4': 999, 'R5': 999}
        # initial position of each Receiver
        self.positionOfR1X = 0
        self.positionOfR1Y = 0

        self.positionOfR3X = 0
        self.positionOfR3Y = 4

        self.positionOfR4X = 4
        self.positionOfR4Y = 4

        self.positionOfR5X = 4
        self.positionOfR5Y = 0
        
        start_server = websockets.serve(self.hello, '10.94.13.155', 8385)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()
        
    #send data to app
    async def hello(self, websocket, path):
        print('hello')
        data = await websocket.recv()
        print(data)
        if data == 'app':
            await websocket.send(str(self.meanPosition))
            # await websocket.send(str(self.nearestRouter))
            return
        
        sia = self.formatData(data)
        ######## mov avg model ########
        #rssi of d0 = 1m
        rssiRefMean = [-58.44]
        nMean = [1.811]

        output = ast.literal_eval(sia[1][1:]) #20 sample data


        if (sia[0] == 'R1' and len(self.buffer1) < 200):
            self.buffer1.extend(output)
        if (sia[0] == 'R3' and len(self.buffer3) < 200):
            self.buffer3.extend(output)
        if (sia[0] == 'R4' and len(self.buffer4) < 200):
            self.buffer4.extend(output)
        if (sia[0] == 'R5' and len(self.buffer5) < 200):
            self.buffer5.extend(output)

        self.buffers = [self.buffer1, self.buffer3, self.buffer4, self.buffer5]

        routerCoord = [[self.positionOfR1X, self.positionOfR1Y], [self.positionOfR3X, self.positionOfR3Y],
                       [self.positionOfR4X, self.positionOfR4Y], [self.positionOfR5X, self.positionOfR5Y]]

        self.bufferlens = [len(self.buffer1),len(self.buffer3),len(self.buffer4),len(self.buffer5)]

        if(self.bufferlens.count(200) == 4): #make sure all 4 routers have 200 samples

            ###########################################################################################
            ############################### for moving avg 200 samples ####################################
            ###########################################################################################
            for j in range(len(self.buffers)):
                rssiMean = numpy.mean(self.buffers[j])
                distanceMean = 10 ** ((rssiMean - (rssiRefMean[0])) / (-10 * nMean[0]))
                self.routers[list(self.routers.keys())[j]] = distanceMean
                print("mov avg {}".format(self.routers))

            ##### Nearest Router #####
            pi = list(self.routers.values())
            # check which pi receives the lowest distance (highest RSSI)
            self.nearestRouter = list(self.routers.keys())[pi.index(min(pi))]
            print('Nearest Router:', self.nearestRouter)
            ################################################################################
            ################################## Trilateration ###############################
            ################################################################################
            pi = list(self.routers.values())
            routerUse = [0, 1, 2, 3]


            ################################################################################
            ########################## Moving average trilat ###############################
            ################################################################################

            #remove the far raspi
            mi = pi.index(max(pi))
            print('################## Moving Average ###################')
            print('remove router index:', mi)
            routerUse.remove(mi)
            self.meanPosition = self.calculate_position(routerCoord[routerUse[0]][0],
                                                        routerCoord[routerUse[0]][1],
                                                        routerCoord[routerUse[1]][0],
                                                        routerCoord[routerUse[1]][1],
                                                        routerCoord[routerUse[2]][0],
                                                        routerCoord[routerUse[2]][1],
                                                        float(pi[routerUse[0]]), float(pi[routerUse[1]]),
                                                        float(pi[routerUse[2]]))
            #just log to analyze
            print('Mov Avg list1:', self.buffers[routerUse[0]])
            print('Mov Avg list2:', self.buffers[routerUse[1]])
            print('Mov Avg list3:', self.buffers[routerUse[2]])
            print('Mov Avg RESULT:', self.meanPosition)

    def formatData(self, data):
        output = data.split(' :')
        return output


    def calculate_position(self, x1, y1, x2, y2, x3, y3, distance_from_r1, distance_from_r2, distance_from_r3):
        # Variable according to triangulation -> in thesis

        a = (-2.0 * x1) + (2.0 * x2)
        b = (-2.0 * y1) + (2.0 * y2)
        c = pow(distance_from_r1, 2) - pow(distance_from_r2, 2) - pow(x1, 2) + \
            pow(x2, 2) - pow(y1, 2) + pow(y2, 2)

        d = (-2. * x2) + (2.0 * x3)
        e = (-2. * y2) + (2.0 * y3)
        f = pow(distance_from_r2, 2) - pow(distance_from_r3, 2) - pow(x2, 2) + \
            pow(x3, 2) - pow(y2, 2) + pow(y3, 2)

        x_of_tracker = ((c * e) - (f * b)) / ((e * a) - (b * d))
        y_of_tracker = ((c * d) - (a * f)) / ((b * d) - (a * e))

        pos = [x_of_tracker, y_of_tracker]

        return pos


    async def send(self, websocket, path):
        position = ''
        await websocket.send(position)


s = Server()
