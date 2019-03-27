routers = {'R1': 999, 'R3': 999, 'R4': 999, 'R5': 999}
buffers = [5,6,7,8]
for j in range(len(buffers)):
                routers[list(routers.keys())[j]] = 5
print("mov avg {}".format(routers))