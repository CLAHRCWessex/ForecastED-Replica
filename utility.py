#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 21:06:03 2018

@author: tm3y13
"""

import math
import numpy as np

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



    


class discrete_dist(object):
    """
    Encapsulates a discrete distribution
    """
    def __init__(self, elements, probabilities):
        self.elements = elements
        self.probabilities = probabilities
        
        self.validate_lengths(elements, probabilities)
        self.validate_probs(probabilities)
        
        
        
    def validate_lengths(self, elements, probs):
        if (len(elements) != len(probs)):
            raise ValueError('Elements and probilities arguments must be of the same length')
            
    def validate_probs(self, probs):
        if(sum(probs) != 1):
            raise ValueError('Probabilities must sum to 1')
        
    def sample(self):
        return np.random.choice(self.elements, p=self.probabilities)


