#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 18:56:42 2018

@author: tm3y13
"""

import simpy

import ForecastED as fed
from ForecastED import discrete_dist
from utility import normal_moments_from_lognormal


#Experiment setup

RUN_TIME = 60*8

#resource counts
CUBICLE_N = 10

#treatment time paramters for lognormal
MEAN_TREATMENT = 150
SIGMA_TREATMENT = 2

#arrival distibution parameters (exp)
MEAN_IAT = 10

#Priority distribution parameters
PRIORITY_ELEMENTS = [1, 2, 3, 4, 5]
PRIORITY_PROBS = [0.2, 0.3, 0.3, 0.15, 0.05]


    
MEAN_TREATMENT, SIGMA_TREATMENT = normal_moments_from_lognormal(MEAN_TREATMENT, 
                                                                SIGMA_TREATMENT**2)


if __name__ == "__main__":
    env = simpy.Environment()
    ed_cubicles = simpy.PriorityResource(env, capacity=CUBICLE_N)
    treat_proc = fed.EvaluationAndTreatment(env, MEAN_TREATMENT, 
                                            SIGMA_TREATMENT)
    
    priority_dist = discrete_dist(PRIORITY_ELEMENTS, PRIORITY_PROBS)
    
    source = fed.PatientSource(env, MEAN_IAT, ed_cubicles, 
                               treat_proc, priority_dist)
    
  
    model = fed.ForecastED(env, source, ed_cubicles)
    model.run(RUN_TIME)

