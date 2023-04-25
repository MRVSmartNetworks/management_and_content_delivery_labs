from sub.micro_data_center import MicroDataCenter
from sub.cloud_data_center import CloudDataCenter
import random
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from queue import Queue, PriorityQueue
import time as tm

"""
Version:
              .o.       
             .888.      
            .8"888.     
           .8' `888.    
          .88ooo8888.   
         .8'     `888.  
        o88o     o8888o 
"""

"""
Procedure:
- Initialize objects of classes MicroDataCenter and CloudDataCenter
- Initialize FES
- Run main loop having set the simulation time

Keep in mind:
- Different arrivals and departures depending on the data center
  - arrival_micro -> arrival in micro data center, arrival_cloud -> arrival in cloud data center
  - (& same for departures)

ARRIVALS:
- Parameters ('event_type[1]'):
  - Name
  - Type of client

DEPARTURES:
- Parameters ('event_type[1]'):
  - Name
  - Server ID (for the server that will process packet)

"""

def printResults(sim_time, mdc, cdc, plots=False):
    """
    printResults
    ---
    Used to read and display the measurements done during the simulation.
    
    This function extracts the measures from the 'data' attributes of the 
    2 queues.

    ### Input parameters
    - sim_time: total simulation time
    - mdc: 'MicroDataCenter' class object
    - cdc: 'CloudDataCenter' class object
    """
    # Task 1(version A). Analysis of the waiting delay
    if plots:
        cdc.data.waitingDelayHist(zeros=True, mean_value=False, img_name="./images/task1_waiting-delays-cdc.png")
        cdc.data.waitingDelayHist(zeros=False, mean_value=True, img_name="./images/task1_waiting-delays-no-zeros-cdc.png")
    """ 
    Some observations on the plot (param: dep_micro: 3s, arr_micro: 10s, dep_cloud: 5s):
    - Very few bins (the method sets n_bins=sqrt(unique values)), which means that few elements 
    are actually arriving to the cloud data center
    - approx. exponential shape (without zeros considered) - this is fine, since the service time is 
    exp, so waiting time is a residual of exponential... (as in lab 1 I guess, more like gamma 
    distributions)
    """

    # Task 2. Analysis of the micro data center buffer size impact on 
    # the performance
    out_dict = {}
    # Count losses of MDC:
    out_dict["losses_MDC"]

    
    return 1

def run(sim_time, tx_delay, fract, q1_len=20, q2_len=10, results=False, plots=False):
    """ 
    Run
    ---
    Paramaters:
        - sim_time: simulation time 
        - tx_delay: transimssion delay between MicroDataCenter and CloudDataCenter
        - fract: fraction of packets of type B
    """
    FES = PriorityQueue()

    MDC = MicroDataCenter(
        serv_t=3.0,
        arr_t=10.0, 
        queue_len=q1_len, 
        n_server=1, 
        event_names=["arrival_micro", "departure_micro"])
    
    CDC = CloudDataCenter(
        serv_t=5.0, 
        arr_t=10.0, 
        queue_len=q2_len, 
        n_server=1, 
        event_names=["arrival_cloud", "departure_cloud"])
    
    # Pick at random the first packet given the fraction of B
    type_pkt = MDC.rand_pkt_type(fract)
    
    # Simulation time 
    time = 0

    FES.put((0, ["arrival_micro", type_pkt, 0]))

    while time < sim_time:
        # a = tm.time()
        (time, event_type) = FES.get()
        # b = tm.time()
        # print(f"Time to extract last: {b-a}")
        print(f"Current time: {time} - event: {event_type}")

        # tm.sleep(2)

        if event_type[0] == "arrival_micro":
            MDC.arrival(time, FES, event_type)

        elif event_type[0] == "arrival_cloud":
            CDC.arrival(time, FES, event_type)

        elif event_type[0] == "departure_micro":
            MDC.departure(time, FES, event_type, tx_delay)
        
        elif event_type[0] == "departure_cloud":
            CDC.departure(time, FES, event_type)
    
    if results or plots:
        # Might be used later for returning the results in multi-run simulations
        if plots:
            return printResults(sim_time, MDC, CDC, plots=True)
        else:
            return printResults(sim_time, MDC, CDC, plots=False)
    else:
        return 0

if __name__ == "__main__":
    random.seed(1)
    
    sim_time = 50000
    tx_delay = 0.5
    fract = 0.5
    run(sim_time, tx_delay, fract, plots=True)

    ###########################
    do_iter = False

    if do_iter:
        # Iterations
        n_iter = 15
        seeds = random.sample(range(1, 10*n_iter), n_iter)

        q1_lengths = [2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40]

        tmp_res = []

        for i in range(n_iter):
            random.seed(seeds[i])
            tmp_res.append(run(sim_time, tx_delay, fract))
