'''
    Attempt at making http request to the horizons database for getting the asteroids' states
'''

import requests
import json
import pyorb
import numpy as np

au2m = 1.496e11
nSmallBodies = 660000 # checked 17/03/2024

# horizon database url
url = 'https://ssd-api.jpl.nasa.gov/sbdb.api'

# do a http request to get the orbital info of all small bodies
for id in range(1, 25):#nSmallBodies + 1):
    # build and send request
    httpCommand = f"{url}?sstr={id}&sat=1"
    r = requests.get(httpCommand)

    # convert json to python dictionary
    dict = json.loads(r.text)

    #debug
    print("\nID: %i" %id)
    print(dict)

    # get the orbital elements from the dict
    # 0: e
    # 1: a
    # 2: perihelion distance
    # 3: i
    # 4: longitude of ascending node
    # 5: argument of perihelion
    # 6: mean anomaly
    orb = pyorb.Orbit(
        M0           = pyorb.M_sol,
        G            = pyorb.get_G('m', 'kg', 's'),
        degrees      = True,
        type         = 'mean',
        num          = 1,
        epoch        = float(dict['orbit']['epoch']),
        a            = float(dict['orbit']['elements'][1]['value']) * au2m,
        e            = float(dict['orbit']['elements'][0]['value']),
        i            = float(dict['orbit']['elements'][3]['value']),
        omega        = float(dict['orbit']['elements'][5]['value']),
        Omega        = float(dict['orbit']['elements'][4]['value']),
        mean_anomaly = float(dict['orbit']['elements'][6]['value'])
    )

    print(float(dict['orbit']['elements'][6]['value']))

'''
    PARALLELIZE GET REQUESTS!

    FIX THE EPOCH!
'''

# Dump request to file
#np.savetxt('asteroidStates.csv', kepler_states, fmt='%f')