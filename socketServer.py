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
        '''
        self.c1routers = {'R1': 999, 'R3': 999, 'R4': 999, 'R5': 999}
        self.c2routers = {'R1': 999, 'R3': 999, 'R4': 999, 'R5': 999}
        self.c3routers = {'R1': 999, 'R3': 999, 'R4': 999, 'R5': 999}
        '''
        # initial position of each Receiver
        self.positionOfR1X = 0
        self.positionOfR1Y = 0

        self.positionOfR3X = 0
        self.positionOfR3Y = 4

        self.positionOfR4X = 4
        self.positionOfR4Y = 4

        self.positionOfR5X = 4
        self.positionOfR5Y = 0
        
        start_server = websockets.serve(self.hello, '10.94.6.158', 8385)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()
        
    #send data to app
    async def hello(self, websocket, path):
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
        '''
        ######## cluster model ########
        rssiRefMeanCluster = [[-48.3787], [-52.7188], [-66.2946]]  # [[c1 angle0],[c2 angle0],[c3 angle0]]
        nMeanCluster = [[1.8128], [2.6148], [1.9121]]
        '''
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
            '''
            ###########################################################################################
            ############################### for kmeans 200 samples ####################################
            ###########################################################################################
            for j in range(len(self.buffers)):
                clusters = self.kmeansClustering(self.buffers[j])
                for i in range(len(clusters)):
                    rssiMean = numpy.mean(clusters[i])
                    print('cluster', i + 1, rssiMean)
                    distanceMean = 10 ** ((rssiMean - (rssiRefMeanCluster[i][0])) / (-10 * nMeanCluster[i][0]))
                    if (i == 0):
                        self.c1routers[list(self.routers.keys())[j]] = distanceMean
                        print("c1 {}".format(self.c1routers))
                    elif (i == 1):
                        self.c2routers[list(self.routers.keys())[j]] = distanceMean
                        print("c2 {}".format(self.c2routers))
                    else:
                        self.c3routers[list(self.routers.keys())[j]] = distanceMean
                        print("c3 {}".format(self.c3routers))
'''
            ################################################################################
            ################################## Trilateration ###############################
            ################################################################################
            pi = list(self.routers.values())
            routerUse = [0, 1, 2, 3]
'''
            c1pi = list(self.c1routers.values())
            c2pi = list(self.c2routers.values())
            c3pi = list(self.c3routers.values())
            routerUseC1 = [0, 1, 2, 3];
            routerUseC2 = [0, 1, 2, 3];
            routerUseC3 = [0, 1, 2, 3];
'''

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
'''
            ####################################################################################
            ######################### kmeans 200 sample trilateration ##########################
            ####################################################################################
            ma = c1pi.index(max(c1pi))
            print('################## Cluster1 ###################')
            print('remove router index:', ma)
            routerUseC1.remove(ma)
            print('C1 list1:', self.buffers[routerUseC1[0]])
            print('C1 list2:', self.buffers[routerUseC1[1]])
            print('C1 list3:', self.buffers[routerUseC1[2]])
            print('C1 RESULT:',
                  self.calculate_position(routerCoord[routerUseC1[0]][0], routerCoord[routerUseC1[0]][1],
                                          routerCoord[routerUseC1[1]][0], routerCoord[routerUseC1[1]][1],
                                          routerCoord[routerUseC1[2]][0], routerCoord[routerUseC1[2]][1],
                                          float(c1pi[routerUseC1[0]]), float(c1pi[routerUseC1[1]]),
                                          float(c1pi[routerUseC1[2]])))

            ma = c2pi.index(max(c2pi))
            print('################## Cluster2 ###################')
            print('remove router index:', ma)
            routerUseC2.remove(ma)
            print('C2 list1:', self.buffers[routerUseC2[0]])
            print('C2 list2:', self.buffers[routerUseC2[1]])
            print('C2 list3:', self.buffers[routerUseC2[2]])
            print('C2 RESULT:',
                  self.calculate_position(routerCoord[routerUseC2[0]][0], routerCoord[routerUseC2[0]][1],
                                          routerCoord[routerUseC2[1]][0], routerCoord[routerUseC2[1]][1],
                                          routerCoord[routerUseC2[2]][0], routerCoord[routerUseC2[2]][1],
                                          float(c2pi[routerUseC2[0]]), float(c2pi[routerUseC2[1]]),
                                          float(c2pi[routerUseC2[2]])))

            ma = c3pi.index(max(c3pi))
            print('################## Cluster3 ###################')
            print('remove router index:', ma)
            routerUseC3.remove(ma)
            print('C3 list1:', self.buffers[routerUseC3[0]])
            print('C3 list2:', self.buffers[routerUseC3[1]])
            print('C3 list3:', self.buffers[routerUseC3[2]])
            print('C3 RESULT:',
                  self.calculate_position(routerCoord[routerUseC3[0]][0], routerCoord[routerUseC3[0]][1],
                                          routerCoord[routerUseC3[1]][0], routerCoord[routerUseC3[1]][1],
                                          routerCoord[routerUseC3[2]][0], routerCoord[routerUseC3[2]][1],
                                          float(c3pi[routerUseC3[0]]), float(c3pi[routerUseC3[1]]),
                                          float(c3pi[routerUseC3[2]])))


            ###########################################################################################
            ############################### filter only distance <= sqrt(20) #################################
            ###########################################################################################
            movAvgDist = list(self.routers.values())
            c1Dist = list(self.c1routers.values())
            c2Dist = list(self.c2routers.values())
            c3Dist = list(self.c3routers.values())

            for i in range(len(movAvgDist)):
                if(movAvgDist[i] > math.sqrt(20) and movAvgDist[i] != max(movAvgDist)):
                    if(i==0):
                        self.routers['R1'] = math.sqrt(20)
                    elif (i == 1):
                        self.routers['R3'] = math.sqrt(20)
                    elif (i == 2):
                        self.routers['R4'] = math.sqrt(20)
                    else:
                        self.routers['R5'] = math.sqrt(20)
            for i in range(len(c1Dist)):
                if(c1Dist[i] > math.sqrt(20) and c1Dist[i] != max(c1Dist)):
                    if(i==0):
                        self.c1routers['R1'] = math.sqrt(20)
                    elif (i == 1):
                        self.c1routers['R3'] = math.sqrt(20)
                    elif (i == 2):
                        self.c1routers['R4'] = math.sqrt(20)
                    else:
                        self.c1routers['R5'] = math.sqrt(20)
            for i in range(len(c2Dist)):
                if(c2Dist[i] > math.sqrt(20) and c2Dist[i] != max(c2Dist)):
                    if(i==0):
                        self.c2routers['R1'] = math.sqrt(20)
                    elif (i == 1):
                        self.c2routers['R3'] = math.sqrt(20)
                    elif (i == 2):
                        self.c2routers['R4'] = math.sqrt(20)
                    else:
                        self.c2routers['R5'] = math.sqrt(20)
            for i in range(len(c3Dist)):
                if(c3Dist[i] > math.sqrt(20) and c3Dist[i] != max(c3Dist)):
                    if(i==0):
                        self.c3routers['R1'] = math.sqrt(20)
                    elif (i == 1):
                        self.c3routers['R3'] = math.sqrt(20)
                    elif (i == 2):
                        self.c3routers['R4'] = math.sqrt(20)
                    else:
                        self.c3routers['R5'] = math.sqrt(20)

            ################################################################################
            ################################## Trilateration (bound) ###############################
            ################################################################################
            pi = list(self.routers.values())
            routerUse = [0, 1, 2, 3];

            c1pi = list(self.c1routers.values())
            c2pi = list(self.c2routers.values())
            c3pi = list(self.c3routers.values())
            routerUseC1 = [0, 1, 2, 3];
            routerUseC2 = [0, 1, 2, 3];
            routerUseC3 = [0, 1, 2, 3];

            ################################################################################
            ########################## Moving average trilat (bound) ###############################
            ################################################################################
            mi = pi.index(max(pi))
            print('################## Moving Average (bound) ###################')
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
            print('Mov Avg list1:', self.buffers[routerUse[0]])
            print('Mov Avg list2:', self.buffers[routerUse[1]])
            print('Mov Avg list3:', self.buffers[routerUse[2]])
            print('Mov Avg RESULT (bound):', self.meanPosition)

            ####################################################################################
            ######################### kmeans 200 sample trilateration (bound)##########################
            ####################################################################################
            ma = c1pi.index(max(c1pi))
            print('################## Cluster1 (bound) ###################')
            print('remove router index:', ma)
            routerUseC1.remove(ma)
            print('C1 list1:', self.buffers[routerUseC1[0]])
            print('C1 list2:', self.buffers[routerUseC1[1]])
            print('C1 list3:', self.buffers[routerUseC1[2]])
            print('C1 RESULT (bound):',
                  self.calculate_position(routerCoord[routerUseC1[0]][0], routerCoord[routerUseC1[0]][1],
                                          routerCoord[routerUseC1[1]][0], routerCoord[routerUseC1[1]][1],
                                          routerCoord[routerUseC1[2]][0], routerCoord[routerUseC1[2]][1],
                                          float(c1pi[routerUseC1[0]]), float(c1pi[routerUseC1[1]]),
                                          float(c1pi[routerUseC1[2]])))

            ma = c2pi.index(max(c2pi))
            print('################## Cluster2 (bound) ###################')
            print('remove router index:', ma)
            routerUseC2.remove(ma)
            print('C2 list1:', self.buffers[routerUseC2[0]])
            print('C2 list2:', self.buffers[routerUseC2[1]])
            print('C2 list3:', self.buffers[routerUseC2[2]])
            print('C2 RESULT (bound):',
                  self.calculate_position(routerCoord[routerUseC2[0]][0], routerCoord[routerUseC2[0]][1],
                                          routerCoord[routerUseC2[1]][0], routerCoord[routerUseC2[1]][1],
                                          routerCoord[routerUseC2[2]][0], routerCoord[routerUseC2[2]][1],
                                          float(c2pi[routerUseC2[0]]), float(c2pi[routerUseC2[1]]),
                                          float(c2pi[routerUseC2[2]])))

            ma = c3pi.index(max(c3pi))
            print('################## Cluster3 (bound) ###################')
            print('remove router index:', ma)
            routerUseC3.remove(ma)
            print('C3 list1:', self.buffers[routerUseC3[0]])
            print('C3 list2:', self.buffers[routerUseC3[1]])
            print('C3 list3:', self.buffers[routerUseC3[2]])
            print('C3 RESULT (bound):',
                  self.calculate_position(routerCoord[routerUseC3[0]][0], routerCoord[routerUseC3[0]][1],
                                          routerCoord[routerUseC3[1]][0], routerCoord[routerUseC3[1]][1],
                                          routerCoord[routerUseC3[2]][0], routerCoord[routerUseC3[2]][1],
                                          float(c3pi[routerUseC3[0]]), float(c3pi[routerUseC3[1]]),
                                          float(c3pi[routerUseC3[2]])))
            ###### clear buffers #######
            self.buffer1 = []
            self.buffer3 = []
            self.buffer4 = []
            self.buffer5 = []


        #############################################################

        '''
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

'''
    def kmeansClustering(self, y):
        y = numpy.array(y)
        x = numpy.array([1] * len(y))
        data = numpy.array(list(zip(x, y))).reshape(len(x), 2)

        # KMeans algorithm
        K = 3
        kmeans_model = KMeans(n_clusters=K).fit(data)
        # clusters
        c1 = []
        c2 = []
        c3 = []
        for i, l in enumerate(kmeans_model.labels_):
            if (l == 0):
                c1.append(y[i])
            elif (l == 1):
                c2.append(y[i])
            else:
                c3.append(y[i])

        order = [c1, c2, c3]
        c3 = order.pop(order.index(min(order)))
        c1 = order.pop(order.index(max(order)))
        c2 = order[0]

        return [c1, c2, c3]
'''

    async def send(self, websocket, path):
        position = ''
        await websocket.send(position)


s = Server()
