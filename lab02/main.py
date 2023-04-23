from sub.micro_data_center import MicroDataCenter
from sub.cloud_data_center import CloudDataCenter
import random
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from queue import Queue, PriorityQueue

"""
TODO:
- Initialize objects of classes MicroDataCenter and CloudDataCenter
- Initialize FES
- Run main loop having set the simulation time

Keep in mind:
- Different arrivals and departures depending on the data center
  - arrival_micro -> arrival in micro data center, arrival_cloud -> arrival in cloud data center
  - (& same for departure)

ARRIVALS:
- Parameters ('event_type[1]'):
  - Name
  - Type of client

DEPARTURES:
- Parameters ('event_type[1]'):
  - Name
  - Server ID (for the server that will process packet)

"""



def run(sim_time, tx_delay, fract):
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
        serv_t = 3.0,
        arr_t= 10.0, 
        queue_len=10, 
        n_server=1, 
        event_names=["arrival_micro", "departure_micro"])
    
    CDC = CloudDataCenter(
        serv_t = 5.0, 
        arr_t= 10.0, 
        queue_len=20, 
        n_server=1, 
        event_names=["arrival_cloud", "departure_cloud"])
    
    # pick at random the first packet givent the fraction
    type_pkt = MDC.rand_pkt_type()
    
    # Simulation time 
    time = 0

    FES.put((0, ["arrival_micro", type_pkt, 0]))

    while time < sim_time:
        (time, event_type) = FES.get()

        if event_type[0] == "arrival_micro":
            MDC.arrival(time, FES, event_type)

        elif event_type[0] == "arrival_cloud":
            CDC.arrival(time, FES, event_type, MDC)

        elif event_type[0] == "departure_micro":
            MDC.departure(time, FES, event_type, tx_delay, CDC)
        
        elif event_type[0] == "departure_cloud":
            CDC.departure(time, FES, event_type)

if __name__ == "__main__":
    sim_time = 500000
    tx_delay = 0.5
    fract= 0.5
    run(sim_time, tx_delay, fract)
