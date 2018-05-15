#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 18:56:42 2018

@author: tm3y13
"""

import simpy

import ForecastED as fed
from utility import normal_moments_from_lognormal


#Parameters 

RUN_TIME = 500
CUBICLE_N = 10

#treatment time paramters for lognormal
MEAN_TREATMENT = 150
SIGMA_TREATMENT = 2

MEAN_IAT = 10

    
MEAN_TREATMENT, SIGMA_TREATMENT = normal_moments_from_lognormal(MEAN_TREATMENT, 
                                                                SIGMA_TREATMENT**2)



if __name__ == "__main__":
    env = simpy.Environment()
    ed_cubicles = simpy.Resource(env, capacity=CUBICLE_N)
    treat_proc = fed.EvaluationAndTreatment(env, MEAN_TREATMENT, SIGMA_TREATMENT)
    source = fed.PatientSource(env, MEAN_IAT, ed_cubicles, treat_proc)
  
    model= fed.ForecastED(env, source, ed_cubicles)
    model.run(500)

