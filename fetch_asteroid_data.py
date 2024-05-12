'''
    Attempt at making http request to the horizons database for getting the asteroids' states
'''

import requests
import json
import pyorb
import asyncio
import aiohttp
import time
import numpy as np



# ========================= #
# === SYNCHRONOUS CALLS === #
# ========================= #

au2m = 1.496e11
nSmallBodies = 660000 # checked 17/03/2024

# horizon database url
url = 'https://ssd-api.jpl.nasa.gov/sbdb.api'

commands = [f"{url}?sstr={id+1}&sat=1" for id in range(10)]
'''
t0 = time.time()
data = []
for i, cmd in enumerate(commands):
    r = requests.get(cmd)
    data.append(r.json())
    print(f'Current request nbr: {i+1}')
t1 = time.time()
print(f'Total time elapsed: {t1-t0}')
'''

# ========================== #
# === ASYNCHRONOUS CALLS === #
# ========================== #

async def get(session, id):
    url = f'https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={id+1}&sat=1'
    response = await session.request('GET', url=url)
    if response.status == 200:
        content = await response.read()
        data = json.loads(content)
        fetch_success = True
        #print(f'Succesfully retrieved data for id {id}')
        return data, id, fetch_success
    else:
        fetch_success = False
        #print(f'Failed to retrieve data for id {id}, with status code {response.status}')
        return id, fetch_success

async def main(ids):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for id in ids:
            tasks.append(get(session, id))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


if __name__ == '__main__':
    n_ids = 100000
    n_successes = 0
    t0 = time.time()
    n_step = 10000
    faulty_ids = []
    data = [0] * n_ids
    for j in range(0, n_ids, n_step):
        t1 = time.time()
        ids = [(j+i+1) for i in range(n_step)]
        while len(ids) > 0:
            res = asyncio.run(main(ids))
            for result in res:
                if result[-1] == True:
                    id = result[-2]-1 # indexing starts at 1 in horizons database
                    data[id] = result[0]
                    ids.remove(result[-2])
                    n_successes += 1
            #print(f'Amount of ids successfully retrieved: {step-len(ids)}/{step}')
        t2 = time.time()
        t_step = t2-t1
        t_tot  = t2-t0
        print(f'\nAmount of ids successfully retrieved: {n_successes}/{n_ids}')
        print(f'Step elapsed time: {t_step}')
        print(f'Total elapsed time: {t_tot}')
        print(f'Step Average time per id: {t_step / n_step}')
        print(f'Total Average time per id: {t_tot / n_successes}')
    #print(data, len(data))

    orb = []
    for entry in data:
        orb.append(pyorb.Orbit(
        M0           = pyorb.M_sol,
        G            = pyorb.get_G('m', 'kg', 's'),
        degrees      = True,
        type         = 'mean',
        epoch        = float(entry['orbit']['epoch']),
        a            = float(entry['orbit']['elements'][1]['value']) * au2m,
        e            = float(entry['orbit']['elements'][0]['value']),
        i            = float(entry['orbit']['elements'][3]['value']),
        omega        = float(entry['orbit']['elements'][5]['value']),
        Omega        = float(entry['orbit']['elements'][4]['value']),
        mean_anomaly = float(entry['orbit']['elements'][6]['value'])
        ))

    #for orbit in orb:
        #print(orbit)
        
'''
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

'''
    PARALLELIZE GET REQUESTS!

    FIX THE EPOCH!
'''

# Dump request to file
#np.savetxt('asteroidStates.csv', kepler_states, fmt='%f')