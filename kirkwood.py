from pyorb.kepler import cart_to_kep
import numpy as np
import matplotlib.pyplot as plt
import csv

m2au = 6.6846e-12

"""
    PLOTTING SHENANIGANS
"""

fig, axes = plt.subplots(1,4)

"""
    IMPORT INITIAL STATE
"""
state = np.empty((6,), dtype=np.float64)
lineCount = 0
with open('input.csv', 'r', newline='') as dataFile:
    csvReader = csv.reader(dataFile)
    for row in csvReader:
        lineCount += 1

xPosIni = []
yPosIni = []
zPosIni = []
xVelIni = []
yVelIni = [] 
zVelIni = []
aIni    = []
lineCount = 0
with open('input.csv', 'r', newline='') as dataFile:
    csvReader = csv.reader(dataFile)
    for row in csvReader:
        xPosIni.append(float(row[0]))
        yPosIni.append(float(row[1]))
        zPosIni.append(float(row[2]))
        xVelIni.append(float(row[3]))
        yVelIni.append(float(row[4]))
        zVelIni.append(float(row[5]))
        
        lineCount += 1
        
for i in range(lineCount):
    state = np.array([xPosIni[i], yPosIni[i], zPosIni[i], xVelIni[i], yVelIni[i], zVelIni[i]])
    kepState = cart_to_kep(state)
    aIni.append(kepState[0] * m2au)
    xPosIni[i] *= m2au
    yPosIni[i] *= m2au
    zPosIni[i] *= m2au

A = np.linspace(0, 6, 100)
N_Ini = np.zeros(len(A))

for i in range(10, lineCount):
    for j in range(len(A)-1):
      if (A[j] < aIni[i] and aIni[i] < A[j+1]):
           N_Ini[j] += 1 

axes[0].plot(A, N_Ini)
axes[0].set_xlabel('Semi-major axis [AU]')
axes[0].set_ylabel('Number of asteroids')
axes[0].set_title('Initial state')

axes[1].scatter(xPosIni[10:], yPosIni[10:], s=0.5)
axes[1].scatter(xPosIni[0], yPosIni[0], color='yellow')
axes[1].scatter(xPosIni[1], yPosIni[1], color='brown')
axes[1].scatter(xPosIni[2], yPosIni[2], color='magenta')
axes[1].scatter(xPosIni[3], yPosIni[3], color='green')
axes[1].scatter(xPosIni[4], yPosIni[4], color='orange')
axes[1].scatter(xPosIni[5], yPosIni[5], color='lime')
axes[1].scatter(xPosIni[6], yPosIni[6], color='darkorange')
axes[1].scatter(xPosIni[7], yPosIni[7], color='cyan')
axes[1].scatter(xPosIni[8], yPosIni[8], color='purple')
axes[1].scatter(xPosIni[9], yPosIni[9], color='red')
axes[1].add_patch(plt.Circle((0,0), 1.6, fill=False))
axes[1].add_patch(plt.Circle((0,0), 5, fill=False))
axes[1].set_aspect('equal')
axes[1].set_xlim([-7, 7])
axes[1].set_ylim([-7, 7])




# """
#     IMPORT FINAL STATE
# """

state = np.empty((6,), dtype=np.float64)
lineCount = 0
with open('output.csv', 'r', newline='') as dataFile:
    csvReader = csv.reader(dataFile)
    for row in csvReader:
        lineCount += 1

xPosFin = []
yPosFin = []
zPosFin = []
xVelFin = []
yVelFin = [] 
zVelFin = []
aFin    = []
lineCount = 0
with open('output.csv', 'r', newline='') as dataFile:
    csvReader = csv.reader(dataFile)
    for row in csvReader:
        xPosFin.append(float(row[0]))
        yPosFin.append(float(row[1]))
        zPosFin.append(float(row[2]))
        xVelFin.append(float(row[3]))
        yVelFin.append(float(row[4]))
        zVelFin.append(float(row[5]))
        
        lineCount += 1
        
for i in range(lineCount):
    state = np.array([xPosFin[i], yPosFin[i], zPosFin[i], xVelFin[i], yVelFin[i], zVelFin[i]])
    kepState = cart_to_kep(state)
    aFin.append(kepState[0] * m2au)
    xPosFin[i] *= m2au
    yPosFin[i] *= m2au
    zPosFin[i] *= m2au

N_Fin = np.zeros(len(A))

for i in range(10, lineCount):
    for j in range(len(A)-1):
      if (A[j] < aFin[i] and aFin[i] < A[j+1]):
           N_Fin[j] += 1 

axes[2].plot(A, N_Ini, label='initial state')
axes[2].plot(A, N_Fin, label='final state')
axes[2].set_xlabel('Semi-major axis [AU]')
axes[2].set_ylabel('Number of asteroids')
axes[2].set_title('Final state')
axes[2].legend()

axes[3].scatter(xPosFin[10:], yPosFin[10:], s=0.5)
axes[3].scatter(xPosFin[0], yPosFin[0], color='yellow')
axes[3].scatter(xPosFin[1], yPosFin[1], color='brown')
axes[3].scatter(xPosFin[2], yPosFin[2], color='magenta')
axes[3].scatter(xPosFin[3], yPosFin[3], color='green')
axes[3].scatter(xPosFin[4], yPosFin[4], color='orange')
axes[3].scatter(xPosFin[5], yPosFin[5], color='lime')
axes[3].scatter(xPosFin[6], yPosFin[6], color='darkorange')
axes[3].scatter(xPosFin[7], yPosFin[7], color='cyan')
axes[3].scatter(xPosFin[8], yPosFin[8], color='purple')
axes[3].scatter(xPosFin[9], yPosFin[9], color='red')
axes[3].add_patch(plt.Circle((0,0), 1.6, fill=False))
axes[3].add_patch(plt.Circle((0,0), 5, fill=False))
axes[3].set_aspect('equal')
axes[3].set_xlim([-7, 7])
axes[3].set_ylim([-7, 7])

plt.get_current_fig_manager().full_screen_toggle()
plt.savefig('graphs/solarSystemPlot', format='png')
plt.show()