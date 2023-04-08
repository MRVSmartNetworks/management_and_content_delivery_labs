#!/usr/bin/python3

import random
import numpy as np
from queue import Queue, PriorityQueue
from sub.measurements import Measure
from sub.client import Client
from sub.server import Server
import matplotlib.pyplot as plt
from scipy.stats import t
from sub.utilities import *

"""
General program for sinluating a queuing system.
Parameters:
- SERVICE
- ARRIVAL
- QUEUE_LEN
- SIM_TIME
"""

# ******************************************************************************
# Constants
# ******************************************************************************
TYPE1 = 1 

SIM_TIME = 500000

# ******************************************************************************
# Additional methods:

def addClient(time, FES, queue, serv, queue_len, n_server, serv_t):
    """
    Decide whether the user can be added.
    Need to look at the QUEUE_LEN parameter.
    This method is called by the 'arrival' subroutine.
    """
    global users, data

    if queue_len is not None:
        # Limited length
        if users < queue_len:
            users += 1
            # create a record for the client
            client = Client(TYPE1,time)
            # insert the record in the queue
            queue.append(client)
            
            # If there are less clients than servers, it means that the 
            # new client can directly be served
            # It may also be that the number of servers is unlimited 
            # (new client always finds a server)
            if n_server is None or users<=n_server:

                # sample the service time
                service_time, serv_id = serv.evalServTime()
                #service_time = 1 + random.uniform(0, SEVICE_TIME)

                # schedule when the client will finish the server
                FES.put((time + service_time, ["departure", serv_id]))
                serv.makeBusy(serv_id)
                
                if n_server is not None:
                    # Update the beginning of the service
                    data.serv_busy[serv_id]['begin_last_service'] = time

                # Update the waiting time for the client which starts to be served straight away
                # Get the client - not extracting:
                cli = queue[0]
                data.waitingDelaysList.append(time - cli.arrival_time)

        else:
            data.countLosses += 1
    else:
        # Unlimited length
        users += 1
    
        # create a record for the client
        client = Client(TYPE1,time)

        # insert the record in the queue
        queue.append(client)

        # If there are less clients than servers, it means that the 
        # new client can directly be served
        if n_server is None or users<=n_server:

            # sample the service time
            service_time, serv_id = serv.evalServTime()
            #service_time = 1 + random.uniform(0, SEVICE_TIME)

            # schedule when the client will finish the server
            FES.put((time + service_time, ["departure", serv_id]))
            serv.makeBusy(serv_id)

            if n_server is not None:
                # Update the beginning of the service
                data.serv_busy[serv_id]['begin_last_service'] = time
            
            # Update the waiting time for the client which starts to be served straight away
            # Get the client - not extracting:
            cli = queue[0]
            data.waitingDelaysList.append(time - cli.arrival_time)

# arrivals *********************************************************************
def arrival(time, FES, queue, serv, queue_len,n_server, arr_t, serv_t):
    """
    arrival
    ---
    Perform operations needed at arrival.
    In particular, the new user is added to the queuing 
    system and the measurements are updated.
    
    Input parameters:
    - time: current time, extracted from the event in the FES.
    - FES: (priority queue) future event set (for scheduling). Used to place 
    the next scheduled arrival.
    - queue: (list) containing all users which are currently inside the 
    system (both waiting and being served).
    """
    global users
    global data
    
    assert (len(queue) == users), "The len of the queue and number of clients don't match"

    #print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )
    
    # cumulate statistics
    data.arr += 1
    data.ut += users*(time-data.oldT)
    data.avgBuffer += max(0, users - n_server)*(time-data.oldT)
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/arr_t)
    
    # schedule the next arrival
    FES.put((time + inter_arrival, ["arrival"]))

    ################################
    addClient(time, FES, queue, serv, queue_len, n_server, serv_t)
    ################################

# ******************************************************************************

# departures *******************************************************************
def departure(time, FES, queue, serv_id, serv, n_server, arr_t, serv_t):
    """
    departure
    ---
    Perform the operations needed at a departure (end of service).
    Specifically, this method updates the measurements and removes the served
    client from the system, then it possibly adds another client to the service.
    Input parameters:
    - time: current time, extracted from the event in the FES.
    - FES: (priority queue) future event set (for scheduling). Used to place 
    the next scheduled arrival.
    - queue: (list) containing all users which are currently inside the 
    system (both waiting and being served).
    """
    global users
    global data

    #print("Departure no. ",data.dep+1," at time ",time," with ",users," users" )
        
    # cumulate statistics
    data.dep += 1
    data.ut += users*(time-data.oldT)
    data.avgBuffer += max(0, users - n_server)*(time-data.oldT)

    data.oldT = time
    
    if len(queue) > 0:
        # get the first element from the queue
        client = queue.pop(0)

        # Make its server idle
        serv.makeIdle(serv_id)

        if n_server is not None:
            # Update cumulative server busy time
            
            # Add to the cumulative time the time difference between now (service end)
            # and the beginning of the service
            # print(data.serv_busy[serv_id]['cumulative_time'])
            data.serv_busy[serv_id]['cumulative_time'] += (time - data.serv_busy[serv_id]['begin_last_service'])
        
        # do whatever we need to do when clients go away
        
        data.delay += (time-client.arrival_time)
        data.delaysList.append(time-client.arrival_time)
        users -= 1
    
    # Update time
    data.oldT = time

    can_add = False

    # See whether there are more clients in the line
    if n_server is not None:
        if users >= n_server:
            can_add = True
    elif users > 0:
        can_add = True

    ########## SERVE ANOTHER CLIENT #############
    if can_add:
        # Sample the service time
        service_time, new_serv_id = serv.evalServTime()

        new_served = queue[0]

        data.waitingDelaysList.append(time-new_served.arrival_time)
        data.waitingDelaysList_no_zeros.append(time-new_served.arrival_time)

        # Schedule when the service will end
        FES.put((time + service_time, ["departure", new_serv_id]))
        serv.makeBusy(new_serv_id)

        if n_server is not None:
            # Update the beginning of the service
            data.serv_busy[new_serv_id]['begin_last_service'] = time
        
# ******************************************************************************
# simulation run function
# ******************************************************************************
def run(serv_t = 5.0, arr_t = 5.0, queue_len = None, n_server = 1, server_policy = "first_idle",seed=1):

    global users
    global data
    ###### Check - the number of servers cannot be unlimited if QUEUE_LEN is finite
    if queue_len is not None and n_server is None:
        """ NOTE: the number of server 'wins' - it forces the queue length to be infinite """
        queue_len = None
    
    # The following contains the list of all clients currently present in the 
    # system (waiting + served):
    MM_system=[]
    users = 0
    random.seed(seed)

    data = Measure(0,0,0,0,0,0, n_server)

    # Simulation time 
    time = 0

    # List of events in the form: (time, type)
    FES = PriorityQueue()

    # Schedule the FIRST ARRIVAL at t=0
    FES.put((0, ["arrival"]))

    # Create servers (class)
    servers = Server(n_server, serv_t, policy=server_policy)

    # Simulate until the simulated time reaches a constant
    while time < SIM_TIME:
        (time, event_type) = FES.get()

        if event_type[0] == "arrival":
            arrival(time, FES, MM_system, servers, queue_len, n_server, arr_t, serv_t)

        elif event_type[0] == "departure":
            departure(time, FES, MM_system, event_type[1], servers, n_server, arr_t, serv_t)
    
    return MM_system, data, time

# ******************************************************************
# main  ************************************************************
# ******************************************************************
if __name__ == "__main__":
    """ 
    PARAMETERS:
        - n_server: indicates the number of servers in the system
                    If None: unlimited n. of servers
        - serv_t: is the average service time; service rate = 1/SERVICE
        - arr_t: is the average inter-arrival time; arrival rate = 1/ARRIVAL
        - load=serv_t/arr_t: This relationship holds for M/M/1
        - queue_len: defines the maximum number of elements in the system
                 If None: unlimited queue
    SIMULATION OPTIONS:
        - single_run: run a single run with fixed parameters
        - change_arr_t: launch multiple runs on different values of the arrival rate
        - multi_vs_single: comparison between MM1 vs MM2 systems
        - change_queue_l: launch multiple runs on different queue length values
     
    """
    single_run = False
    change_arr_t = True
    multi_vs_single = False
    change_queue_l = False

    if single_run:
        n_server = 1
        serv_t = 2.0 # is the average service time; service rate = 1/SERVICE
        arr_t = 6.0 # is the average inter-arrival time; arrival rate = 1/ARRIVAL
        if n_server is not None:
            load=serv_t/(arr_t*n_server)    # Valid at steady-state

        # queue_len defines the maximum number of elements in the system
        # If None: unlimited queue
        queue_len = 10
        if queue_len is not None:
            if n_server is not None:
                queue_len = max(queue_len, n_server)        # This ensure compatible parameters
            else:
                queue_len = None
        MM_system, data, time = run(serv_t, arr_t, queue_len, n_server)
        printResults(n_server, queue_len, arr_t, serv_t, users, data, time, MM_system, SIM_TIME)
        
    if change_arr_t:
        # system parameters
        arr_t_list = range(3, 7)
        queue_len = 10
        n_server = 1
        serv_t = 5.0

        # confidence interval 
        n_iter = 6 # number of iteration for confidence interval
        conf_level = 0.99
        intervals = []
        avgDelay_mean = []
        
        data_list = []

        for arr_t in arr_t_list:
            
            MM_system, data, time = run(arr_t=arr_t, serv_t=serv_t, n_server=n_server, queue_len=queue_len)
            data_list.append(data)
            # loop to evalaute confidence interval
            data_conf_int = []
            for i in range(n_iter):
                MM_system, data, time = run(arr_t=arr_t, serv_t=serv_t, n_server=n_server, queue_len=queue_len, seed=None)
                data_conf_int.append(data)

            avgDelay = [data.delay/data.dep for data in data_conf_int]
            avgDelay_mean.append(np.mean(avgDelay))
            intervals.append(t.interval(conf_level, n_iter-1, np.mean(avgDelay), np.std(avgDelay)/np.sqrt(n_iter)))
            
        # metrics plots on different arrival rates
        plotArrivalRate(arr_t_list, data_list, [queue_len, n_server, serv_t])

        # confidence interval for no. of losses
        plt.figure()
        plt.title(f"Confidence intervals for average delay - df={n_iter-1} - conf_level={conf_level}")
        plt.plot([1./x for x in arr_t_list], avgDelay_mean)
        plt.fill_between([1./x for x in arr_t_list], list(zip(*intervals))[0], list(zip(*intervals))[1], color='r', alpha=.2)
        plt.grid()
        plt.show()

    if multi_vs_single:
        # system parameters
        arr_t = 6.0
        queue_len = 10
        serv_t = 5.0
        
        MM1, data1, time1 = run(arr_t=arr_t, serv_t=serv_t, n_server=1, queue_len=queue_len) # MM1 system
        MM2, data2, time2 = run(arr_t=arr_t, serv_t=serv_t, n_server=2, queue_len=queue_len) # MM2 system
        printResults(1, "first-idle", queue_len, arr_t, serv_t, users, data1, time1, MM1, SIM_TIME)
        printResults(2, "first_idle", queue_len, arr_t, serv_t, users, data2, time2, MM2, SIM_TIME)

    if change_queue_l:

        queue_len_list = list(range(1, 12))
        data_list = []
        arr_t = 6.0
        serv_t = 5.0
        n_server = 2
        for queue_len in queue_len_list:
            MM2, data, time2 = run(arr_t=arr_t, serv_t=serv_t, n_server=n_server, queue_len=queue_len) # MM2 system
            data_list.append(data)

        plotQueueLen(queue_len_list, data_list, [arr_t, n_server, serv_t])

            
            
