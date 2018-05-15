#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 21:06:03 2018

@author: tm3y13
"""

import math

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
        treat_proc = EvaluationAndTreatment(env, MEAN_TREATMENT, SIGMA_TREATMENT)
        patient = Patient(env, i, ed_cubicles, treat_proc)
        env.process(patient.execute())
        #self.env.process(patient(self.env, i, self.ed_cubicles))
        #env.process(patient(env, i, ed_cubicles))