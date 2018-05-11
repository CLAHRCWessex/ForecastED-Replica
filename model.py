#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 18:56:42 2018

@author: tm3y13
"""

import simpy
import itertools
import numpy as np
import math


RUN_TIME = 500

CUBICLE_N = 10

#treatment time paramters for lognormal
MEAN_TREATMENT = 150
SIGMA_TREATMENT = 2




MEAN_IAT = 10



def patient(env, unique_id, ed_cubicles):
    """A patient enteres the ED, waits for a treatment cubicle,
    has treatment and then leaves"""    
    
    print('Patient {0} enters the ED at {1}'.format(unique_id, env.now))
    
    
    
    with ed_cubicles.request() as req:
        start_wait = env.now
        # Request one of the ed cubicles for treatment
        yield req
        
        cubicle_wait = env.now - start_wait
        
        print('Patient {0}: starts treatment = {1} minutes;' 
              + 'wait = {2}'.format(unique_id,env.now, cubicle_wait))

        
        # The reatment time
        treatment_duration= np.random.lognormal(MEAN_TREATMENT, SIGMA_TREATMENT)
        print('Patient {0} treatment time ={1}.'.format(unique_id,
              treatment_duration))
        yield env.timeout(treatment_duration)

        print('Patient {0} leaves the ED at {1} minutes.'.format(unique_id,env.now))


        
def patient_generator(env, ed_cubicles):
    """Generate new patients that arrive at the ED."""
    for i in itertools.count():
        yield env.timeout(np.random.exponential(MEAN_IAT))
        env.process(patient(env, i, ed_cubicles))
        
        
def observe_queue(env, res, interval):
   for i in itertools.count():
       yield env.timeout(interval)
       print('QUEUE LENGTH: {0}'.format(len(res.queue)))
       

def observe_service(env, res, interval):
   for i in itertools.count():
       yield env.timeout(interval)
       print('IN SERVICE: {0}'.format(len(res.users)))
    


def normal_moments_from_lognormal(m, v):
    """
    Returns mu and sigma of normal distribution
    underlying a lognormal with mean m and variance v
    
    @m = mean of lognormal distribution
    @v = variance of lognormal distribution
    """
    phi = math.sqrt(v + m**2)
    mu = math.log(m**2/phi)
    sigma = math.sqrt(math.log(phi**2/m**2))
    return mu, sigma
    
    

MEAN_TREATMENT, SIGMA_TREATMENT = normal_moments_from_lognormal(MEAN_TREATMENT, 
                                                                SIGMA_TREATMENT**2)

env = simpy.Environment()
ed_cubicles = simpy.Resource(env, capacity=CUBICLE_N)


env.process(patient_generator(env, ed_cubicles))
env.process(observe_queue(env, ed_cubicles, 10)) 
env.process(observe_service(env, ed_cubicles, 10))    

env.run(until=RUN_TIME)
