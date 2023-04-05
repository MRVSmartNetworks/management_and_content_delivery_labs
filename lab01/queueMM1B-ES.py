#!/usr/bin/python3

import random
from queue import Queue, PriorityQueue
from sub.measurements import Measure

# ******************************************************************************
# Constants
# ******************************************************************************

SERVICE = 10.0 # SERVICE is the average service time; service rate = 1/SERVICE
ARRIVAL = 5.0 # ARRIVAL is the average inter-arrival time; arrival rate = 1/ARRIVAL
LOAD=SERVICE/ARRIVAL # This relationship holds for M/M/1

TYPE1 = 1 

SIM_TIME = 500000

arrivals = 0
users = 0
BusyServer = False # True: server is currently busy; False: server is currently idle

# The queue is modeled as a list
# The clients are appended at arrival and are removed at the end of the service
MM1 = []

# "B" - maximum number of elements in the system
QUEUE_LEN = 1000
        
# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self,type,arrival_time):
        self.type = type
        self.arrival_time = arrival_time

# ******************************************************************************
# Server
# ******************************************************************************
class Server(object):

    # constructor
    def __init__(self):

        # whether the server is idle or not
        self.idle = True


# ******************************************************************************

# arrivals *********************************************************************
def arrival(time, FES, queue):
    global users
    
    #print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )
    
    assert (users == len(queue)), "The length of the queue is different from the number of users"

    # cumulate statistics
    data.arr += 1
    data.ut += users*(time-data.oldT)
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)
    
    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    # Add record if the number of users is less than the max. allowed
    if users < QUEUE_LEN:
        users += 1
        # create a record for the client
        client = Client(TYPE1,time)
        # insert the record in the queue
        queue.append(client)
        
        # If the server was idle before the last arrival, the newly arrived 
        # client can already be served
        if users==1:
            
            # sample the service time
            service_time = random.expovariate(1.0/SERVICE)
            #service_time = 1 + random.uniform(0, SEVICE_TIME)

            # schedule when the client will finish the server
            FES.put((time + service_time, "departure"))
    else:
        data.countLosses += 1

# ******************************************************************************

# departures *******************************************************************
def departure(time, FES, queue):
    global users

    #print("Departure no. ",data.dep+1," at time ",time," with ",users," users" )
    
    assert (users == len(queue)), "The length of the queue is different from the number of users"

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

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))

        
# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************

random.seed(42)

data = Measure(0,0,0,0,0,0)

# the simulation time 
time = 0

# the list of events in the form: (time, type)
FES = PriorityQueue()


# schedule the first arrival at t=0
FES.put((0, "arrival"))

################################################################################
# simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type) = FES.get()

    if event_type == "arrival":
        arrival(time, FES, MM1)

    elif event_type == "departure":
        departure(time, FES, MM1)
################################################################################

# print output data
print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
      data.arr,"- No. of departures =",data.dep)

print("Load: ", SERVICE/ARRIVAL)
print("\nArrival rate: ",data.arr/time," - Departure rate: ",data.dep/time)

print("\nAverage number of users: ",data.ut/time)

print("Average delay: ",data.delay/data.dep)
print("Actual queue size: ",len(MM1))

if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)
    
print(f"Number of losses: {data.countLosses}")

data.queuingDelayHist()
data.plotQueuingDelays()
