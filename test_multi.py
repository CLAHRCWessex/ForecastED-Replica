# -*- coding: utf-8 -*-
"""
Created on Wed May 30 21:53:17 2018

@author: tm3y13
"""

import multiprocessing as mp
import time

import simpy


def testproc(env, num):
    for i in range(4):
        yield env.timeout(1)
        time.sleep(0.1)  # Do hard work
        print(num, env.now)


def simulate(num):
    env = simpy.Environment()
    env.process(testproc(env, num))
    env.run()


with mp.Pool(mp.cpu_count()) as pool:
    pool.map(simulate, range(7))