'''
    AUTHOR  : Louis-Hendrik BARBOUTIE
    CONTACT : louis.barboutie@gmail.com
    INPUT   : None
    RETURNS : Two csv files, one with the state vectors and one with the epochs of observations
    SYNOPSIS: This script performs asynchronous calls to the JPL Horizons small body database
              to fetch the state vectors of all the catalogued asteroids. 
              The large amount of requests makes synchronous requests not viable. Since the 
              database frequently returns 503 status errors upon requests, a while loop is 
              necessary to resend the requests which failed.
'''

import requests
import json
import pyorb
import asyncio
import aiohttp
import time
import numpy as np

# ========================== #
# === PHYSICAL CONSTANTS === #
# ========================== #

au2m = 1.496e11

# ========================== #
# === ASYNCHRONOUS CALLS === #
# ========================== #

# StackOverFlow magic right there
async def get(session, id):
    '''
        Asynchronous function to fetch a single id
        Returns data only upon successful request
    '''
    url = f'https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={id}&sat=1'
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
    '''
        Asynchronous function to send a bundle of requests to the server
        First a session is created, and all requests are sent at once in
        a list. 
        Returns the data once all tasks have completed (successfully or not)
    '''
    async with aiohttp.ClientSession() as session:
        tasks = []
        for id in ids:
            tasks.append(get(session, id))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

# ================= #
# === MAIN LOOP === #
# ================= #

if __name__ == '__main__':
    
    # clear the files' contents 
    states_file_path = 'asteroidStates.csv'
    epochs_file_path = 'epochs.csv'
    open(states_file_path, 'w').close()
    open(epochs_file_path, 'w').close()

    print('Fetching asteroid states...')

    # open the file in append mode so that saving can be done in steps
    states_file = open(states_file_path, 'a')
    epochs_file = open(epochs_file_path, 'a')
    
    n_ids = 660000
    n_step = 10000
    n_successes_total = 0
    
    t0 = time.time()
    
    for j in range(0, n_ids, n_step):
        t1 = time.time() # initial time for the beginning of the step
        n_successes_step = 0
        data = [] # [0] * n_step
        ids = [(j+i+1) for i in range(n_step)]
        while len(ids) > 0:
            res = asyncio.run(main(ids)) # send the request calls
            for result in res:
                if result[-1] == True:
                    #id = result[-2]-1 # indexing starts at 1 in horizons database
                    data.append(result[0]) # [id] = result[0]
                    ids.remove(result[-2])
                    n_successes_total += 1
                    n_successes_step += 1
            print(f'Amount of ids successfully retrieved: {n_successes_step}/{n_step}')
        
        # debug
        t2 = time.time()
        t_step = t2-t1
        t_tot  = t2-t0
        print(f'Step elapsed time: {t_step}')
        print(f'Total elapsed time: {t_tot}')
        print(f'Step Average time per id: {t_step / n_step}')
        print(f'Total Average time per id: {t_tot / n_successes_total}')
        print(f'Amount of ids successfully retrieved: {n_successes_total}/{n_ids}\n')

        # Store states with the PyOrb's orbit struct for convenience
        # it has built in access to cartesian coordinates
        orbits = []
        for entry in data:
            orbits.append(pyorb.Orbit(M0      = pyorb.M_sol,
                                      G       = pyorb.get_G('m', 'kg', 's'),
                                      degrees = True,
                                      type    = 'mean',
                                      epoch   = float(entry['orbit']['epoch']),
                                      a       = float(entry['orbit']['elements'][1]['value']) * au2m,
                                      e       = float(entry['orbit']['elements'][0]['value']),
                                      i       = float(entry['orbit']['elements'][3]['value']),
                                      omega   = float(entry['orbit']['elements'][5]['value']),
                                      Omega   = float(entry['orbit']['elements'][4]['value']),
                                      anom    = float(entry["orbit"]["elements"][6]["value"]),
            ))

        # Prep the lists for dumping to file
        cartesian_states = [[] for i in range(len(orbits))]
        epochs = [0] * len(orbits)
        for i, orbit in enumerate(orbits):
            epochs[i] = orbit.epoch 
            for element in orbit.cartesian:
                cartesian_states[i].append(element[0])
        
        # Dump request to file
        np.savetxt(states_file, cartesian_states, fmt='%f')
        np.savetxt(epochs_file, epochs, fmt='%f')

    # clean up files
    states_file.close()
    epochs_file.close()