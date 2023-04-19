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

    MDC = MicroDataCenter()
    CDC = CloudDataCenter()
    
    if(random.uniform(0, 1) < fract):
        type_pkt = "B"
    else:
        type_pkt = "A"

    FES.put((0, ["arrival_micro", type_pkt]))

    while time < sim_time:
        (time, event_type) = FES.get()

        if event_type[0] == "arrival_micro":
            MDC.arrival(time, FES, event_type)

        elif event_type[0] == "arrival_cloud":
            CDC.arrival(time, FES, event_type)

        elif event_type[0] == "departure_micro":
            MDC.departure(time, FES, event_type, tx_delay)
        
        elif event_type[0] == "departure_cloud":
            CDC.departure(time, FES, event_type)

if __name__ == "__main__":
    run()
