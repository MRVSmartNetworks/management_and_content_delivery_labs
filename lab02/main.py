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
        cdc.data.waitingDelayHist(zeros=True, mean_value=False, img_name=None)
        cdc.data.waitingDelayHist(zeros=False, mean_value=True, img_name=None)
        mdc.data.plotUsrInTime()
        
        plt.figure(figsize=(8,4))
        plt.plot(np.linspace(1,sim_time, len(mdc.data.arrivalsList)), mdc.queue)
        plt.title("Number of arrival of the system")
        plt.xlabel("Simulation time")
        plt.ylabel("Inter arrival times of the packets")
        plt.show()
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
    #out_dict = {}
    # Count losses of MDC:
    #out_dict["losses_MDC"]
    
    return cdc.data, mdc.data

    

def run(sim_time, fract, serv_t_1=9.0, arr_t=10.0, 
        q1_len=20, n_serv_1 = 1, serv_t_2 = 10.0, 
        q2_len=10,n_serv_2 = 1,results=False, plots=False):
    """ 
    Run
    ---
    Paramaters:
        - sim_time: simulation time 
        - fract: fraction of packets of type B
    """
    FES = PriorityQueue()

    # control if there are more service rate during the simulation
    # and split the simulation proportionally to the no. of service
    # rates
        
    

    MDC = MicroDataCenter(
        serv_t=serv_t_1,
        arr_t=arr_t, 
        queue_len=q1_len, 
        n_server=n_serv_1, 
        event_names=["arrival_micro", "departure_micro"])
    
    CDC = CloudDataCenter(
        serv_t=serv_t_2, 
        arr_t=None, 
        queue_len=q2_len, 
        n_server=n_serv_2, 
        event_names=["arrival_cloud", "departure_cloud"])
    
    # Pick at random the first packet given the fraction of B
    type_pkt = MDC.rand_pkt_type(fract)
    
    # Simulation time 
    if isinstance(arr_t,list):
        step_time = sim_time/len(arr_t)
        step_app = step_time
        i = 0
        MDC.arr_t = arr_t[i]
    else:
        step_time = sim_time
    time = 0

    FES.put((0, ["arrival_micro", type_pkt, 0]))
    
    while time < step_time:
        # a = tm.time()
        (time, event_type) = FES.get()
        # b = tm.time()
        # print(f"Time to extract last: {b-a}")
        #print(f"Current time: {time} - event: {event_type}")

        # tm.sleep(2)
        
        if event_type[0] == "arrival_micro":
            MDC.arrival(time, FES, event_type)

        elif event_type[0] == "arrival_cloud":
            CDC.arrival(time, FES, event_type)

        elif event_type[0] == "departure_micro":
            MDC.departure(time, FES, event_type)
        
        elif event_type[0] == "departure_cloud":
            CDC.departure(time, FES, event_type)
        
        if time > step_time and step_time < sim_time:   # check if the simulation is not finished
            step_time += step_app
            i += 1
            MDC.arr_t = arr_t[i]
    
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
    fract = 0.5
    run(sim_time, fract, results=True)

    ###########################
    do_iter = False
    multi_server = True

    if do_iter:
        # Iterations
        n_iter = 15
        seeds = random.sample(range(1, 10*n_iter), n_iter)

        q1_lengths = [2, 4, 6, 8, 10, 15, 20, 25, 30, 35, 40]

        tmp_res = []

        for i in range(n_iter):
            random.seed(seeds[i])
            tmp_res.append(run(sim_time, fract))
    
    # Task.3 Analysis on packets A average time in the system
    # Threshold T_q to set desired max average time 
    T_q = None
    if T_q is not None:
        # a) Find min serv rate to reduce delay A below T_q
        serv_r_list = np.arange(0.1, 0.8, 0.1)
        min_found = False
        delay_list = []
        for serv_r in serv_r_list:
            res_cdc, res_mdc = run(sim_time, fract, serv_t_1=1./serv_r, results=True)
            delay_A = (res_cdc.delay_A + res_mdc.delay_A)/(res_cdc.dep + res_mdc.dep)
            delay_list.append(delay_A)
            if delay_A < T_q and not min_found:
                print(f"\nMinimum service rate is {serv_r}")
                min_found = True
        plt.figure()
        plt.title("Min serv_r to reduce delay_A below T_q")
        plt.ylabel("delay_A")
        plt.xlabel("serv_rate")
        plt.axhline(T_q, linestyle='--')
        plt.plot(list(serv_r_list), delay_list)
        
        # a) Find min no. of edge nodes to reduce delay A below T_q
        n_serv_list = range(1, 20)
        min_found = False
        delay_list = []
        for n_serv in n_serv_list:
            res_cdc, res_mdc = run(sim_time, fract, n_serv_1=n_serv,serv_t_1=15.0, results=True)
            delay_A = (res_cdc.delay_A + res_mdc.delay_A)/(res_cdc.dep + res_mdc.dep)
            delay_list.append(delay_A)
            if delay_A < T_q and not min_found:
                print(f"\nMinimum no. of edges is {n_serv}")
                min_found = True
        
        plt.figure()
        plt.title("Min n_serv to reduce delay_A below T_q")
        plt.xlabel("no. of servers")
        plt.ylabel("delay_A")
        plt.axhline(T_q, linestyle='--')
        plt.plot(list(n_serv_list), delay_list)
        plt.show()
    
        
    # Task. 4 Analysis of the system with multi-server
    if multi_server:
        arrival_list = [10,6,2,8]
        run(sim_time, fract, arr_t=arrival_list, n_serv_1 = 4, n_serv_2 = 4, results=True, plots=True)
    

            

