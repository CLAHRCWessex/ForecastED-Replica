#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility class for sampling.

Notes: Should I be worried about each object
having its own psuedo random number stream?

"""

import math
import numpy as np
from numpy.random import random_sample
import itertools

def weighted_values(elements, cum_probs, size=1):
    
    return elements[np.digitize(random_sample(size), cum_probs)]

def normal_moments_from_lognormal(m, v):
    """
    Returns mu and sigma of normal distribution
    underlying a lognormal with mean m and variance v
    source: https://blogs.sas.com/content/iml/2014/06/04/simulate-lognormal-data-with-specified-mean-and-variance.html
    
    @m = mean of lognormal distribution
    @v = variance of lognormal distribution
    """
    phi = math.sqrt(v + m**2)
    mu = math.log(m**2/phi)
    sigma = math.sqrt(math.log(phi**2/m**2))
    return mu, sigma


class lognormal_dist(object):
    """
    Encapsulates a lognormal distirbution
    """
    def __init__(self, mean, stdev):
        """
        @mean = mean of the lognormal distribution
        @stdev = standard dev of the lognormal distribution
        """
        mu, sigma = normal_moments_from_lognormal(mean, stdev**2)
        self.mu = mu
        self.sigma = sigma
        
    def sample(self):
        """
        Sample from the normal distribution
        """
        return np.random.lognormal(self.mu, self.sigma)
     


class discrete_dist(object):
    """
    Encapsulates a discrete distribution
    """
    def __init__(self, elements, probabilities):
        self.elements = elements
        self.probabilities = probabilities
        
        self.validate_lengths(elements, probabilities)
        self.validate_probs(probabilities)
        
        self.cum_probs = np.add.accumulate(probabilities)
        
        
    def validate_lengths(self, elements, probs):
        if (len(elements) != len(probs)):
            raise ValueError('Elements and probilities arguments must be of the same length')
            
    def validate_probs(self, probs):
        if(sum(probs) != 1):
            raise ValueError('Probabilities must sum to 1')
        
    def sample(self):
        return weighted_values(self.elements, self.cum_probs)[0]
        #return np.random.choice(self.elements, p=self.probabilities)



def nspp(data):
    """
    Samples from a non-stationary poisson process using
    a piecewise linear rate function.  
    Uses the DIRECT ALGORITHM from
    http://journals.sagepub.com/doi/10.1177/0037549706065514
    
    This needs cleaning up.
    
    At the moment it just assumes that all days of the week
    have the same nspp.  Needs to handle 7 days of week.
    
    @data numpy.array of k segments (rows).  Columns are:
        0. k (for reference)
        1. b_k = upper bound of segment time (e.g. 60 = 0 - 60 minutes)
        2. lambda = average no. arrivals in segement (for reference only)
        3. c_k = cumulative arrivals
        4. r_k = gradient of segment
    """

    k = 1
    S_n = 0
    T_n = 0
    
    max_k = 24
    day = 1

    for n in itertools.count():
       
        u = random_sample(1)[0]
        A = -np.log(u) 
        S_n += A
        
        while(S_n - data[k][3] > 0): 
            if(k < max_k):
                k += 1
            else:
                #out of segments - next day
                k = 1
                S_n = A
                day+=1
                break
            
        T_n = data[k-1][1] + ((S_n - data[k-1][3])/data[k][4])
        
       # print("At yield: {0}: T_n: {1}; T_n_c: {2}; day: {3}".format(n, T_n, T_n + (1440*(day-1)), day))

        yield T_n + (1440*(day-1))
