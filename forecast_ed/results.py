#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 12:49:04 2018

@author: tm3y13
"""


class _ResultsSingleton(object):
    """
    A singleton class for storing results of a simulation model.
    An instance is created when module is loaded.
    The class is the accessed via the ResultsSingleton func.
    This "simulates" the singleton pattern in Python as it would work
    in a statically typed language such as C#
    I.e Only a single instance of this class can be created.
    """

    def __init__(self):
        self.instance = "Instance at %d" % self.__hash__()


_results_singleton = _ResultsSingleton()

def ResultsSingleton(): 
    """
    Returns the results singleton
    """
    return _results_singleton






