'''
    Attempt at making http request to the horizons database for getting the asteroids' states
'''

import requests
import json

nSmallBodies = 660000 # checked 17/03/2024

url = 'https://ssd-api.jpl.nasa.gov/sbdb.api'

# do a http request to get the orbital info of all small bodies
for id in range(1, 10):#nSmallBodies + 1):
    # build and send request
    httpCommand = f"{url}?sstr={id}&sat=1"
    r = requests.get(httpCommand)

    # convert json to python dictionary
    dict = json.loads(r.text)

    print("\nID: %i" %id)

    # get the orbital elements from the dict
    for i in range(11):
        title = dict['orbit']['elements'][i]['title']
        value = dict['orbit']['elements'][i]['value']
        print(title, "=", value) # eccentricity etc.

# Dump request to file
'''
with open('HTTP_test.txt', 'w') as f:
    f.write()
'''