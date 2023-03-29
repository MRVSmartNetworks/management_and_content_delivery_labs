#!/usr/bin/python3

import random
import numpy as np
from queue import Queue, PriorityQueue
from sub.measurements import Measure
from sub.client import Client
from sub.server import Server

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

SERVICE = 5.0 # SERVICE is the average service time; service rate = 1/SERVICE
ARRIVAL = 5.0 # ARRIVAL is the average inter-arrival time; arrival rate = 1/ARRIVAL
LOAD=SERVICE/ARRIVAL # This relationship holds for M/M/1

# QUEUE_LEN defines the maximum number of elements in the system
# If None: unlimited queue
QUEUE_LEN = None

# N_SERVERS indicates the number of servers in the system
# If None: unlimited n. of servers
N_SERVERS = None

###### Check - the number of servers cannot be unlimited if QUEUE_LEN is finite
if QUEUE_LEN is not None and N_SERVERS is None:
    """ NOTE: the number of server 'wins' - it forces the queue length to be infinite """
    QUEUE_LEN = None

TYPE1 = 1 

SIM_TIME = 500000

arrivals=0
users=0

# The following contains the list of all clients currently present in the 
# system (waiting + served):
MM_system=[]

# ******************************************************************************
# Additional methods:

def addClient(time, FES, queue, serv):
    """
    Decide whether the user can be added.
    Need to look at the QUEUE_LEN parameter.

    This method is called by the 'arrival' subroutine.
    """
    global users, data

    if QUEUE_LEN is not None:
        # Limited length
        if users < QUEUE_LEN:
            users += 1
            # create a record for the client
            client = Client(TYPE1,time)
            # insert the record in the queue
            queue.append(client)
            
            # If there are less clients than servers, it means that the 
            # new client can directly be served
            # It may also be that the number of servers is unlimited 
            # (new client always finds a server)
            if N_SERVERS is None or users<=N_SERVERS:
                
                # sample the service time
                service_time, serv_id = serv.evalServTime()
                #service_time = 1 + random.uniform(0, SEVICE_TIME)

                # schedule when the client will finish the server
                FES.put((time + service_time, ["departure", serv_id]))
                serv.makeBusy(serv_id)

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
        if N_SERVERS is None or users<=N_SERVERS:
            
            # sample the service time
            service_time, serv_id = serv.evalServTime()
            #service_time = 1 + random.uniform(0, SEVICE_TIME)

            # schedule when the client will finish the server
            FES.put((time + service_time, ["departure", serv_id]))
            serv.makeBusy(serv_id)
            
            # Update the waiting time for the client which starts to be served straight away
            # Get the client - not extracting:
            cli = queue[0]
            data.waitingDelaysList.append(time - cli.arrival_time)

# arrivals *********************************************************************
def arrival(time, FES, queue, serv):
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
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)
    
    # schedule the next arrival
    FES.put((time + inter_arrival, ["arrival"]))

    ################################
    addClient(time, FES, queue, serv)
    ################################

# ******************************************************************************

# departures *******************************************************************
def departure(time, serv_id, FES, queue, serv):
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
    data.oldT = time
    
    if len(queue) > 0:
        # get the first element from the queue
        client = queue.pop(0)
        
        # do whatever we need to do when clients go away
        
        data.delay += (time-client.arrival_time)
        data.delaysList.append(time-client.arrival_time)
        users -= 1
    
    can_add = False

    # See whether there are more clients in the line
    if N_SERVERS is not None:
        if users >= N_SERVERS:
            can_add = True
    elif users > 0:
        can_add = True

    if can_add:
        # Sample the service time
        service_time, new_serv_id = serv.evalServTime()

        new_served = queue[0]

        data.waitingDelaysList.append(time-new_served.arrival_time)
        data.waitingDelaysList_no_zeros.append(time-new_served.arrival_time)

        # Schedule when the service will end
        FES.put((time + service_time, ["departure", new_serv_id]))
        serv.makeBusy(serv_id)
        
# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************
random.seed(42)

data = Measure(0,0,0,0,0,0)

# Simulation time 
time = 0

# List of events in the form: (time, type)
FES = PriorityQueue()

# Schedule the FIRST ARRIVAL at t=0
FES.put((0, ["arrival"]))

# Create servers (class)
servers = Server(N_SERVERS, SERVICE)

# Simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type) = FES.get()

    if event_type[0] == "arrival":
        arrival(time, FES, MM_system, servers)

    elif event_type[0] == "departure":
        departure(time, event_type[0], FES, MM_system, servers)

# ******************************************************************************
# Print output data ************************************************************
# ******************************************************************************

print("******************************************************************************")
print("MEASUREMENTS: \n\nNo. of users in the queue (at stop): ",users,"\nNo. of total arrivals =",
      data.arr,"- No. of total departures =",data.dep)

print("Load: ",SERVICE/ARRIVAL)
print("\nArrival rate: ",data.arr/time," - Departure rate: ",data.dep/time)

print("\nAverage number of users: ",data.ut/time)

print("\nNumber of losses: ", data.countLosses)

print("Average delay: ",data.delay/data.dep)
print("Actual queue size: ",len(MM_system))

if len(MM_system)>0:
    print("Arrival time of the last element in the queue:",MM_system[len(MM_system)-1].arrival_time)
    
print(f"Average waiting delay: ")
print(f"> Considering clients which are not waiting: {np.average(data.waitingDelaysList)}")
print(f"> Without considering clients which did not wait: {np.average(data.waitingDelaysList_no_zeros)}")

print("******************************************************************************")

data.queuingDelayHist()
data.plotQueuingDelays()
