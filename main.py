#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 18:56:42 2018

@author: tm3y13
"""

import simpy
import pandas as pd
import numpy as np
import scipy as sp
import scipy.stats
import cProfile
import pstats

import forecast_ed.model as mod
from forecast_ed.utility import discrete_dist, lognormal_dist

DISPLAY_PROFILE = True


#Experiment setup

PRINT_TRACE = False
REPLICATIONS = 100

FORECAST_HORIZON = 8
RUN_TIME = 60*FORECAST_HORIZON

#resource counts
CUBICLE_N = 12

#treatment time paramters for lognormal
MEAN_TREATMENT = 150
SIGMA_TREATMENT = 2

#arrival distibution parameters (exp)
MEAN_IAT = 10

#Priority distribution parameters
PRIORITY_ELEMENTS = np.array([1, 2, 3, 4, 5])
PRIORITY_PROBS = np.array([0.2, 0.3, 0.3, 0.15, 0.05])


#Prob patient is admitted (needs to be by triage category)
ADMIT_PROBS = [0.03, 0.10, 0.2, 0.5, 0.9]

MEAN_ADMIT_DELAY = 10
STD_ADMIT_DELAYS = 5




def display_run_results(model):
    """
    Print the results of the run fo the user.
    """
    for r in model.get_results().items():
        print(r)
    
    
def store_run_results(model, a_results, rep):
    """
    Store current run results in a dataframe of all reps
    Potentially this could be stored more efficiently.
    numpy array?
    """
    
    col = 0
    
    for i in model.get_results().items():
        #df_results.loc[rep][i[0]] = i[1]
        a_results[rep][col]  = i[1]
        col += 1
    
    
        
        
        
    
    
def multiple_replications(run_time, n):
    """
    Run multiple replications of the model
    https://stackoverflow.com/questions/45061369/simpy-how-to-run-a-simulation-multiple-times
    https://bitbucket.org/simpy/simpy/issues/71/multiprocessing
    """
    
    #df_results = init_results_df(n)
    a_results = init_results_array(n)
    
    priority_dist = discrete_dist(PRIORITY_ELEMENTS, PRIORITY_PROBS)
    
    treatment_dist = lognormal_dist(MEAN_TREATMENT, SIGMA_TREATMENT)
    
    for rep in range(n):
        print('***** RUNNING REPLICATION {0}'.format(rep+1))
       
        env, ed_cubicles = init_simpy()

        
        treat_proc = mod.Delay(env, treatment_dist)
    
        source = mod.PatientSource(env, 
                                   MEAN_IAT, 
                                   ed_cubicles, 
                                   treat_proc, 
                                   priority_dist,
                                   ADMIT_PROBS)
        
        model = mod.ForecastED(env, source, ed_cubicles)
        model.run(RUN_TIME) 
        
        store_run_results(model, a_results, rep)
        
    return a_results


def init_simpy():
    env = simpy.Environment()
    ed_cubicles = simpy.PriorityResource(env, capacity=CUBICLE_N)
    return env, ed_cubicles
    
    
def init_results_df(n):
    cols = ['Arrivals', 'Mean_Cubicle_Wait', 
            'Std_Cubicle_Wait', 'Mean_Cubicle_Q', 'Mean_Cubicle_Util']
    
    
    return pd.DataFrame(index=np.arange(n), columns=cols)


def init_results_array(n):   
    return np.zeros(shape=(n,5))

    

def mean_confidence_interval(data, confidence=0.95):
    n = len(data)
    m, se = np.mean(data), scipy.stats.sem(data)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return [m, m-h, m+h]



def print_batch_results(a_results):
   
    print('\n*** KPIs from numpy')
    
    cols = ['Arrivals', 'Mean_Cubicle_Wait', 
            'Std_Cubicle_Wait', 'Mean_Cubicle_Q', 'Mean_Cubicle_Util']
    
    df_results = pd.DataFrame(a_results, columns=cols)
    
    kpi = df_results.apply(lambda x: mean_confidence_interval(x), axis=0)
    
    df_kpi = pd.DataFrame.from_items(zip(kpi.index, kpi.values))
    df_kpi = pd.DataFrame(df_kpi.T.as_matrix(), index = df_kpi.T.index, columns=['Mean', 'LCI', 'UCI'])
    
    print(df_kpi)


def _run():
    a_results = multiple_replications(RUN_TIME, REPLICATIONS)


    if 1 < REPLICATIONS:
        print_batch_results(a_results)

   

if __name__ == "__main__":
    mod.set_trace(PRINT_TRACE)
    cProfile.run('_run()', filename = 'pr.txt')
    
    
    if DISPLAY_PROFILE:
        p = pstats.Stats('pr.txt')
        p.sort_stats('cumulative').print_stats(70)
    

#to do:#
# initial conditions of ED 
# number of people in queue, number of people in service (how long etc...)
        
#to do - create a numpy array to store data in - compare this to the 
#performance of pandas dataframe.
    

    

    
        
    
    
    

