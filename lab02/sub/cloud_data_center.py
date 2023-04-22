from sub.server import Server
from sub.client import Client

from sub.queue import Queue

import random


class CloudDataCenter(Queue):
    
    def arrival(self, time, FES, event_type, micro_class):
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

        
        # cumulate statistics
        self.data.arr += 1
        self.data.ut += self.users*(time-self.data.oldT)
        self.data.avgBuffer += max(0, self.users - self.n_server)*(time-self.data.oldT)
        self.data.oldT = time

        # sample the time until the next event
        inter_arrival = random.expovariate(lambd=1.0/self.arr_t)
        self.data.arrivalsList.append(inter_arrival)
        
        # schedule the next arrival
        FES.put((time + inter_arrival, [micro_class.arr_name, self.rand_pkt_type()]))

        ################################
        self.addClient(time, FES, event_type)
        ################################        
