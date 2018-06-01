# -*- coding: utf-8 -*-
"""
Test of the non-stationary poisson process sampling func.
"""

import numpy as np
import simpy

from forecast_ed.sampling import nspp

fname = 'data/arrivals.csv'
data = np.genfromtxt(fname, delimiter=',', skip_header=1)

arrivals = []
                      

def generate(env):
   a = nspp(data)
   
   for time in a:
       iat = time - env.now
       arrivals.append(time)
       print("Now: {0}; IAT: {1}; Next: {2}".format(env.now, iat, env.now+iat))
       yield env.timeout(iat)
       

run_time = 1440*5
time = 0

env = simpy.Environment()
env.process(generate(env))
env.run(until=run_time)

np.savetxt('data.csv', np.array(arrivals), delimiter=',')

