#!/usr/bin/python3

import random
import numpy as np
from queue import Queue, PriorityQueue
from sub.measurements import Measure
from sub.client import Client
from sub.server import Server

# ******************************************************************************
# Constants
# ******************************************************************************

SERVICE = 5.0 # SERVICE is the average service time; service rate = 1/SERVICE
ARRIVAL = 5.0 # ARRIVAL is the average inter-arrival time; arrival rate = 1/ARRIVAL
LOAD=SERVICE/ARRIVAL # This relationship holds for M/M/1

TYPE1 = 1 

SIM_TIME = 500000

arrivals=0
users=0
BusyServer=False # True: server is currently busy; False: server is currently idle

MM1=[]

# ******************************************************************************

# arrivals *********************************************************************
def arrival(time, FES, queue):
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
    
    assert (len(queue) == users), "The len of the queue and number of clients don't match"

    #print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )
    
    # cumulate statistics
    data.arr += 1
    data.ut += users*(time-data.oldT)
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)
    
    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    users += 1
    
    # create a record for the client
    client = Client(TYPE1,time)

    # insert the record in the queue
    queue.append(client)

    # if the server is idle start the service
    if users==1:
        
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)
        #service_time = 1 + random.uniform(0, SEVICE_TIME)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
        
        # Update the waiting time for the client which starts to be served straight away
        # Get the client - not extracting:
        cli = queue[0]
        
        data.waitingDelaysList.append(time - cli.arrival_time)

# ******************************************************************************

# departures *******************************************************************
def departure(time, FES, queue):
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
    
    # see whether there are more clients to in the line
    if users > 0:
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)

        new_served = queue[0]

        data.waitingDelaysList.append(time-new_served.arrival_time)
        data.waitingDelaysList_no_zeros.append(time-new_served.arrival_time)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))

        
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
FES.put((0, "arrival"))

# Simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type) = FES.get()

    if event_type == "arrival":
        arrival(time, FES, MM1)

    elif event_type == "departure":
        departure(time, FES, MM1)

# Print output data
print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
      data.arr,"- No. of departures =",data.dep)

print("Load: ",SERVICE/ARRIVAL)
print("\nArrival rate: ",data.arr/time," - Departure rate: ",data.dep/time)

print("\nAverage number of users: ",data.ut/time)

print("Average delay: ",data.delay/data.dep)
print("Actual queue size: ",len(MM1))

if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)
    
print(f"Average waiting delay: ")
print(f"Considering clients which are not waiting: {np.average(data.waitingDelaysList)}")
print(f"Without considering clients which did not wait: {np.average(data.waitingDelaysList_no_zeros)}")

data.queuingDelayHist()
data.plotQueuingDelays()
