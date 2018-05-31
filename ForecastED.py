#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 21:01:46 2018

@author: tm3y13

Notes: Common ramdom numbers for variance reduction?!!!
"""

import itertools
import numpy as np
from scipy.stats import bernoulli
from numpy.random import binomial


from Results import ResultsSingleton

from utility import lognormal_dist

_trace = True

def set_trace(print_trace):
    global _trace 
    _trace = print_trace


def trace(msg):
    if(_trace):
        print(msg)
        



class ForecastED:
    """
    ForecastED model
    """
    
    def __init__(self, env, source, ed_cubicles):
        """
        @env = simpy.environment
        @source = prococess source
        @ed_cubicles = ed_cubicles resource
        """
        self.env = env
        self.source = source
        self.ed_cubicles = ed_cubicles
        self.init_results_collection()
        
        
    
    def init_results_collection(self):
        self.run_results = {}
        ResultsSingleton().cubicle_waits = []
        ResultsSingleton().arrival_count = 0
        ResultsSingleton().cubicle_queue = []
        ResultsSingleton().cubicle_service = []
        
    
        
    
    def run(self, runtime):
        
        self.env.process(self.source.generate())
        self.env.process(observe_queue(self.env, self.ed_cubicles, 10, ResultsSingleton().cubicle_queue)) 
        self.env.process(observe_service(self.env, self.ed_cubicles, 10, ResultsSingleton().cubicle_service))  
        self.env.run(until=runtime)
        
        self.process_run_results()
    
    
    def process_run_results(self):
        self.run_results['Arrivals'] = ResultsSingleton().arrival_count
        self.run_results['Mean_Cubicle_Wait'] = np.array(ResultsSingleton().cubicle_waits).mean()
        self.run_results['Std_Cubicle_Wait'] = np.array(ResultsSingleton().cubicle_waits).std()
        self.run_results['Mean_Cubicle_Q'] = np.array(ResultsSingleton().cubicle_queue).mean()
        self.run_results['Mean_Cubicle_Util'] = np.array(ResultsSingleton().cubicle_service).mean() / self.ed_cubicles.capacity
    

    def get_results(self):
        return self.run_results
    


class PatientSource(object):
    """
    Arrival of patients to the ED.
    Patients are set a priority on arrival
    
    """
    def __init__(self, env, mean_IAT, 
                 ed_cubicles, treat_proc, priority_dist, p_admit):
        
        self.env = env
        self.mean_IAT = mean_IAT
        self.ed_cubicles = ed_cubicles
        self.treat_proc = treat_proc
        self.priority_dist = priority_dist
        self.p_admit = p_admit
        self.count = 0
        
        
    def generate(self):
        """Generate new patients that arrive at the ED."""
        for i in itertools.count():
            yield self.env.timeout(np.random.exponential(self.mean_IAT))

            priority = self.priority_dist.sample()
            
            if(binomial(1, self.p_admit[priority-1], 1)[0] == 1):
                patient = AdmittedPatient(self.env, i, 
                                             self.ed_cubicles, 
                                             self.treat_proc, 
                                             priority
                                             )
            
            else:
                patient = NonAdmittedPatient(self.env, i, 
                                             self.ed_cubicles, 
                                             self.treat_proc, 
                                             priority
                                             )
            
            self.env.process(patient.execute())
            self.count += 1
            ResultsSingleton().arrival_count += 1
        
        
     
        

class Delay(object):
    
    def __init__(self, env, dist):
        self.env = env
        self.dist = dist
        
    
    def execute(self):
        """A patient undergoes treatment in a ED cubicle """   

        self.on_enter()
        yield self.env.timeout(self.dist.sample())      
        self.on_exit()
        
        
    def on_enter(self):
        """
        On enter logic.  Can be monkey patched as needed
        """
        pass
    
    def on_exit(self):
        """
        On exit logic. Can be monkey patched as needed.
        """
        pass
    


class NonAdmittedPatient(object):
    
    def __init__(self, env, identifer, ed_cubicles, treat_proc, priority=1):
        self.env = env
        self.arrival_time = env.now
        self.identifer = identifer
        self.ed_cubicles = ed_cubicles
        self.treat_proc = treat_proc
        self.priority = priority
        
        
        
    def execute(self):
        """A patient enteres the ED, waits for a treatment cubicle,
        has treatment and then leaves"""    
    
        trace('Patient {0} enters the ED at {1}'.format(self.identifer, 
              self.env.now))
    
        with self.ed_cubicles.request(priority=self.priority) as req:
            start_wait = self.env.now
            # Request one of the ed cubicles for treatment
            yield req
            
            self.cubicle_wait = self.env.now - start_wait
            ResultsSingleton().cubicle_waits.append(self.cubicle_wait)
            
            trace('Patient {0}: starts treatment = {1} minutes; wait = {2}'.format(self.identifer,self.env.now, 
                            self.cubicle_wait))
            
            yield self.env.process(self.treat_proc.execute())
            
            
            trace('Patient {0} leaves the ED at {1} minutes.'
                  .format(self.identifer, self.env.now))



class AdmittedPatient(object):
    
    def __init__(self, env, identifer, ed_cubicles, treat_proc, priority=1):
        self.env = env
        self.arrival_time = env.now
        self.identifer = identifer
        self.ed_cubicles = ed_cubicles
        self.treat_proc = treat_proc
        self.priority = priority
        self.admit_delay = Delay(env, lognormal_dist(10, 10))
        
        
    def execute(self):
        """A patient enteres the ED, waits for a treatment cubicle,
        has treatment and then waits for admission"""    
    
        trace('Patient {0} enters the ED at {1}'.format(self.identifer, 
              self.env.now))
    
        with self.ed_cubicles.request(priority=self.priority) as req:
            start_wait = self.env.now
            # Request one of the ed cubicles for treatment
            yield req
            
            self.cubicle_wait = self.env.now - start_wait
            
            #potentially expensive - is there a way to make this cheaper?
            #would a running mean and stdev be more efficient? 
            ResultsSingleton().cubicle_waits.append(self.cubicle_wait)
            
            trace('Patient {0}: starts treatment = {1} minutes; wait = {2}'.format(self.identifer, self.env.now, 
                            self.cubicle_wait))
            
            yield self.env.process(self.treat_proc.execute())
            
            
            trace('Patient {0} begins waiting for admission at {1} minutes.'
                  .format(self.identifer, self.env.now))
            
            yield self.env.process(self.admit_delay.execute())  
            
            trace('Patient {0} admitted to hospital at {1} minutes.'
                  .format(self.identifer, self.env.now))
            
            



def observe_queue(env, res, interval, results):
   """
   Observe a queue for a resource at a specified interval and store 
   results
   
   @env - Simpy environment
   @res - resource to monitor
   @interval - observation interval
   @results - results list.  stores Q lengths
   """
   for i in itertools.count():
       yield env.timeout(interval)
       trace('QUEUE LENGTH: {0}'.format(len(res.queue)))
       results.append(len(res.queue))
       

def observe_service(env, res, interval, results):
   """
   Observe a how many resources are in use at a specified interval and store 
   results
   
   @env - Simpy environment
   @res - resource to monitor
   @interval - observation interval
   @results - results list. Stores number of users of resource.
   """
   for i in itertools.count():
       yield env.timeout(interval)
       trace('IN SERVICE: {0}'.format(len(res.users)))
       results.append(len(res.users))
       
       
       



    
    
