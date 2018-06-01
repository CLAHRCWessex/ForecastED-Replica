# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 15:30:55 2018

@author: tm3y13
"""

def nspp(data):

    k = 1
    S_n = 0
    T_n = 0
    
    max_k = 24
    day = 1
    flag_day = False
    day_overrun = 0
    
    
    for n in itertools.count():
       
        u = random_sample(1)[0]
        A = -np.log(u) 
        S_n += A
        
        while(S_n - data[k][3] > 0): 
            if(k < max_k):
                k += 1
            else:
                flag_day = True
                break
            
        T_n = data[k-1][1] + ((S_n - data[k-1][3])/data[k][4])
        
        #print("At yield: {0}: T_n: {1}; day: {2}".format(n, T_n, day))
        
        
        
        
        yield T_n - (1440*(day-1)) + day_overrun
        
        if(flag_day==True):
            flag_day = False
            k = 1
            S_n = 0
            day+=1
            #print('previous overrun = {0}'.format(day_overrun))
            day_overrun = T_n - 1440 + day_overrun
            #print('******day over run {0}'.format(day_overrun))