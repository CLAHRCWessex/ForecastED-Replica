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

import ForecastED as fed
from utility import normal_moments_from_lognormal, discrete_dist


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
PRIORITY_ELEMENTS = [1, 2, 3, 4, 5]
PRIORITY_PROBS = [0.2, 0.3, 0.3, 0.15, 0.05]


#Prob patient is admitted (needs to be by triage category)
ADMIT_PROBS = [0.03, 0.10, 0.2, 0.5, 0.9]


MEAN_TREATMENT, SIGMA_TREATMENT = normal_moments_from_lognormal(MEAN_TREATMENT, 
                                                                SIGMA_TREATMENT**2)

def display_run_results(model):
    """
    Print the results of the run fo the user.
    """
    for r in model.get_results().items():
        print(r)
    
    
def store_run_results(model, df_results, rep):
    for i in model.get_results().items():
        df_results.loc[rep][i[0]] = i[1]
    
    
def multiple_replications(run_time, n):
    
    df_results = init_results_df(n)
    
    for rep in range(n):
        print('***** RUNNING REPLICATION {0}'.format(rep+1))
        env = simpy.Environment()
        
        ed_cubicles = simpy.PriorityResource(env, capacity=CUBICLE_N)
        treat_proc = fed.EvaluationAndTreatment(env, MEAN_TREATMENT, 
                                            SIGMA_TREATMENT)
    
        priority_dist = discrete_dist(PRIORITY_ELEMENTS, PRIORITY_PROBS)
    
        source = fed.PatientSource(env, 
                                   MEAN_IAT, 
                                   ed_cubicles, 
                                   treat_proc, 
                                   priority_dist,
                                   ADMIT_PROBS)
        
        model = fed.ForecastED(env, source, ed_cubicles)
        model.run(RUN_TIME) 
        
        store_run_results(model, df_results, rep)
        
    return df_results


def init_results_df(n):
    cols = ['Arrivals', 'Mean_Cubicle_Wait', 
            'Std_Cubicle_Wait', 'Mean_Cubicle_Q', 'Mean_Cubicle_Util']
    
    return pd.DataFrame(index=np.arange(n), columns=cols)
    

def mean_confidence_interval(data, confidence=0.95):
    n = len(data)
    m, se = np.mean(data), scipy.stats.sem(data)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return [m, m-h, m+h]



def print_batch_results(df_results):
    print('\n*** KPIs')
    
    kpi = df_results.apply(lambda x: mean_confidence_interval(x), axis=0)
    
    df_kpi = pd.DataFrame.from_items(zip(kpi.index, kpi.values))
    df_kpi = pd.DataFrame(df_kpi.T.as_matrix(), index = df_kpi.T.index, columns=['Mean', 'LCI', 'UCI'])
    
    print(df_kpi)



if __name__ == "__main__":
    
    fed.set_trace(PRINT_TRACE)
    df_results = multiple_replications(RUN_TIME, REPLICATIONS)
    
    print_batch_results(df_results)
    
    
    

    

    
        
    
    
    

