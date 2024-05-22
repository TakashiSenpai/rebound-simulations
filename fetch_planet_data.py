'''
    AUTHOR  : Louis-Hendrik Barboutie
    CONTACT : louis.barboutie@gmail.com
'''

# ================= #
# === LIBRARIES === #
# ================= #

import astropy.time
import astropy.coordinates
import astropy.units
import numpy as np

# ======================= #
# === TESTING GROUNDS === #
# ======================= #

# observation parameters
epoch = astropy.time.Time('2460400.5', format='jd')
astropy.coordinates.solar_system_ephemeris.set('/home/louis/Documents/IRF/rebound-simulations/de440.bsp')

# select body and time 
coords = astropy.coordinates.get_body_barycentric_posvel('Sun', epoch)

# store the desired parameters as state vector in desired units
pos = []
vel = []
for i in range(3):
    pos.append(coords[0].get_xyz()[i].to_value(astropy.units.kilometer))
    vel.append(coords[1].get_xyz()[i].to_value(astropy.units.kilometer / astropy.units.second))
state = pos + vel

print(state)

# =================== #
# === PLANET DATA === #
# =================== #

from astroquery.jplhorizons import Horizons

# ids of the bodies
# Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn, Neptune, Uranus, Pluto
planet_ids = ['10', '199', '299', '399', '499', '599', '699', '799', '899', '999']
observer = '@10' # heliocentric coordinates

# wipe the file 
open('BarycenterStates.txt', 'w').close()

# make the query to the horizons database
file = open('BarycenterStates.txt', 'a')
state = np.zeros(6)
for id in planet_ids:
    obj = Horizons(id=id, location=observer, epochs=epoch)
    vec = obj.vectors() # table containing the data
    
    # extract the data from the table and set the units
    state[0] = vec['x'].quantity.to_value(astropy.units.kilometer)[0]
    state[1] = vec['y'].quantity.to_value(astropy.units.kilometer)[0]
    state[2] = vec['z'].quantity.to_value(astropy.units.kilometer)[0]
    state[3] = vec['vx'].quantity.to_value(astropy.units.kilometer / astropy.units.second)[0]
    state[4] = vec['vy'].quantity.to_value(astropy.units.kilometer / astropy.units.second)[0]
    state[5] = vec['vz'].quantity.to_value(astropy.units.kilometer / astropy.units.second)[0]
    
    # dump to output file
    np.savetxt(file, state.reshape(1, state.shape[0]), fmt='%f')

file.close()

'''
# ===================== #
# === ASTEROID DATA === #
# ===================== #

from astroquery.jplsbdb import SBDB

# ids of the bodies
asteroids = [i for i in range(1, 10)]

open('asteroidStates.txt', 'w').close()

file = open('asteroidStates.txt', 'a')
for asteroid in asteroids:
    obj = SBDB.query([str(i) for i in range(10)])#, location=location, epochs=epoch)
    vec = obj.vectors()
    
    state[0] = vec['x'].quantity.to_value(astropy.units.kilometer)[0]
    state[1] = vec['y'].quantity.to_value(astropy.units.kilometer)[0]
    state[2] = vec['z'].quantity.to_value(astropy.units.kilometer)[0]
    state[3] = vec['vx'].quantity.to_value(astropy.units.kilometer / astropy.units.second)[0]
    state[4] = vec['vy'].quantity.to_value(astropy.units.kilometer / astropy.units.second)[0]
    state[5] = vec['vz'].quantity.to_value(astropy.units.kilometer / astropy.units.second)[0]
    print(state)
    np.savetxt(file, state.reshape(1, state.shape[0]), fmt='%f')

file.close()
'''