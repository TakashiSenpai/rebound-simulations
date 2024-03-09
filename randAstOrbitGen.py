import pyorb
import numpy as np
import matplotlib.pyplot as plt
import csv
import sys

'''
    ORBIT GENERATION TIME
'''

# common parameters in SI and degrees
au2m   = 149597870700
minDist = 1.6 * au2m
maxDist = 5 * au2m
avgDist = (maxDist + minDist) / 2
width = maxDist - minDist
maxEcc = 0.1
varEcc = 0.05
avgInc = 0
varInc = 15

nOrb = int(sys.argv[1])
orb = pyorb.Orbit(
    M0      = pyorb.M_sol,
    G       = pyorb.get_G('m', 'kg', 's'),
    num     = nOrb,
    degrees = True,
    a       = np.random.normal(avgDist, scale=width/4, size=nOrb), 
    e       = 0.0, # np.random.normal(maxEcc, scale=varEcc, size=nOrb), 
    i       = np.random.normal(avgInc, scale=varInc, size=nOrb),
    omega   = np.random.rand(nOrb) * 360, 
    Omega   = np.random.rand(nOrb) * 360, 
    anom    = np.linspace(0, 360, num=nOrb), # change this to random
)

'''
    SAVE ASTEROID STATES TO FILE
'''

with open('asteroidStates.csv', 'w') as dataFile:
    csvWriter = csv.writer(dataFile)
    for i in range(nOrb):
        row = []
        for j in range(6):
            row.append(str(orb[i].cartesian[j][0]))
        csvWriter.writerow(row)

# use numpy savetxt with comma delimiter

'''
    PLOTTING GO BRRRRRRR
'''

x = []
y = []

for i in range(nOrb):
    x.append(orb[i].cartesian[0])
    y.append(orb[i].cartesian[1])

fig, axes = plt.subplots()
axes.add_patch(plt.Circle((0,0), minDist, fill=False))
axes.add_patch(plt.Circle((0,0), maxDist, fill=False))
axes.scatter(x, y)
axes.set_aspect('equal')
plt.get_current_fig_manager().full_screen_toggle()
plt.show()