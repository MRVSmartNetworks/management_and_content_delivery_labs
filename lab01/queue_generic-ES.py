#!/usr/bin/python3

import random
import numpy as np
from queue import Queue, PriorityQueue
from sub.measurements import Measure
from sub.client import Client
from sub.server import Server
import matplotlib.pyplot as plt
import scipy.stats as st

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

SIM_TIME = 50000

img_path = "report/images/"         # To be filled with desired name

# ******************************************************************************
# Additional methods:

def addClient(time, FES, queue, serv, queue_len, n_server):
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
            data.n_usr_t.append((users, time))
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
                service_time, serv_id = serv.evalServTime(type="uniform")
                data.servicesList.append(service_time)
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
            # Lost client
            data.countLosses += 1
    else:
        # Unlimited length
        users += 1
        data.n_usr_t.append((users, time))

        # create a record for the client
        client = Client(TYPE1,time)

        # insert the record in the queue
        queue.append(client)

        # If there are less clients than servers, it means that the 
        # new client can directly be served
        if n_server is None or users<=n_server:

            # sample the service time
            service_time, serv_id = serv.evalServTime(type="uniform")
            data.servicesList.append(service_time)
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
def arrival(time, FES, queue, serv, queue_len,n_server, arr_t):
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
    data.arrivalsList.append(inter_arrival)
    
    # schedule the next arrival
    FES.put((time + inter_arrival, ["arrival"]))

    ################################
    addClient(time, FES, queue, serv, queue_len, n_server)
    ################################

# ******************************************************************************

# departures *******************************************************************
def departure(time, FES, queue, serv_id, serv, n_server):
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
        data.n_usr_t.append((users, time))
    
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
        service_time, new_serv_id = serv.evalServTime(type="uniform")
        data.servicesList.append(service_time)

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
def run(serv_t=5.0, arr_t=5.0, queue_len=None, n_server=1):
    """
    run
    ---
    Run the simulation of the queuing system.

    Input parameters:
    - serv_t: average service time (1/serv_rate)
    - arr_t: average inter-arrival time (1/arr_rate)
    - queue_len: maximum queue length (if None then infinite queue)
    - n_server: number of servers (if None then infinite queue)
    """
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
    random.seed(42)

    data = Measure(0,0,0,0,0,0, n_server)

    # Simulation time 
    time = 0

    # List of events in the form: (time, type)
    FES = PriorityQueue()

    # Schedule the FIRST ARRIVAL at t=0
    FES.put((0, ["arrival"]))

    # Create servers (class)
    servers = Server(n_server, serv_t, policy="first_idle")

    # Simulate until the simulated time reaches a constant
    while time < SIM_TIME:
        (time, event_type) = FES.get()

        if event_type[0] == "arrival":
            arrival(time, FES, MM_system, servers, queue_len, n_server, arr_t)

        elif event_type[0] == "departure":
            departure(time, FES, MM_system, event_type[1], servers, n_server)
    
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
     
    """
    single_run = True
    change_arr_t = True

    if single_run:
        n_server = 5
        
        arr_rate = 10.
        # serv_rate = [10., 7., 5., 2., 1.]
        serv_rate = 100.

        arr_t = 1./arr_rate # is the average inter-arrival time; arrival rate = 1/ARRIVAL
        
        if isinstance(serv_rate, int) or isinstance(serv_rate, float):
            serv_t = 1./serv_rate # is the average service time; service rate = 1/SERVICE
        elif isinstance(serv_rate, list):
            serv_t = [1./x for x in serv_rate]
        
        if n_server is not None and (isinstance(serv_t, int) or isinstance(serv_t, float)):
            load = serv_t/(arr_t*n_server)    # Valid at steady-state
        elif n_server is not None and isinstance(serv_t, list):
            load = arr_rate/sum(serv_rate)

        # queue_len defines the maximum number of elements in the system
        # If None: unlimited queue
        queue_len = 20
        if queue_len is not None:
            if n_server is not None:
                queue_len = max(queue_len, n_server)        # This ensure compatible parameters
            else:
                queue_len = None
        ########################################
        MM_system, data, time = run(serv_t, arr_t, queue_len, n_server)
        ########################################
        print("******************************************************************************")

        print("SYSTEM PARAMETERS:\n")
        print(f"Number of servers: {n_server}\nMaximum queue length: {queue_len}")
        print(f"Packet arrival rate: {1./arr_t}\nService rate(s): {serv_rate}")

        print(f"\nSimulation time: {SIM_TIME}")

        print("******************************************************************************")
        print("MEASUREMENTS: \n\nNo. of users in the queue (at stop): ",users,"\nNo. of total arrivals =",
            data.arr,"- No. of total departures =",data.dep)
         
        print("Load (theor.): ", load)
        print("\nMeasured arrival rate: ",data.arr/time,"\nMeasured departure rate: ",data.dep/time)

        print("\nAverage number of users: ",data.ut/time)

        print("\nNumber of losses: ", data.countLosses)

        print("Average delay: ",data.delay/data.dep)
        print("Actual queue size: ",len(MM_system))

        if len(MM_system)>0:
            print("Arrival time of the last element in the queue:",MM_system[len(MM_system)-1].arrival_time)
        else:
            print("The queue was empty at the end of the simulation")
            
        print(f"\nAverage waiting delay: ")
        print(f"> Considering clients which are not waiting: {np.average(data.waitingDelaysList)}")
        print(f"> Without considering clients which did not wait: {np.average(data.waitingDelaysList_no_zeros)}")

        print(f"\nAverage buffer occupancy: {data.avgBuffer/time}" )

        print(f"\nLoss probability: {data.countLosses/data.arr}")

        if n_server is not None:
            # The server occupancy only makes sense if the number of servers is 
            # finite (and we can define) a policy for the servers utilization
            print('\nBusy Time: ')
            for i in range(n_server):
                print(f"> Server {i+1} - cumulative service time: {data.serv_busy[i]['cumulative_time']}")

        print("******************************************************************************")

        # Create name for images (used to determine the parameters)
        if n_server is None:
            n_s = "inf"
        else:
            n_s = str(n_server)

        if queue_len is None:
            n_c = "inf"
        else:
            n_c = str(queue_len)

        fileinfo = f"{n_s}_serv_{n_c}_queue"
        
        data.plotUsrInTime(img_name=img_path+"usr_time_"+fileinfo+".png")
        data.queuingDelayHist(mean_value="on", img_name=img_path+"hist_delay_"+fileinfo+".png")
        data.plotQueuingDelays(img_name=img_path+"delay_time_"+fileinfo+".png")
        data.plotServUtilDelay(sim_time=SIM_TIME, policy="first_idle", img_name=img_path+"serv_util_"+fileinfo+".png")
        data.plotArrivalsHist(mean_value="on", img_name=img_path+"inter_arr_"+fileinfo+".png")
        data.plotServiceTimeHist(mean_value="on", img_name=img_path+"serv_time_"+fileinfo+".png")
    
    if change_arr_t:
        arr_t_list = range(1, 20)
        queue_len = 10
        ndroppacket = []
        Narrivals = []
        Ndepartures = []
        for arr_t in arr_t_list:
            MM_system, data, time = run(arr_t=arr_t, queue_len=queue_len)
            ndroppacket.append(data.countLosses)
            Ndepartures.append(data.dep)
            Narrivals.append(data.arr)
            
        plt.title("Narr & Ndep")
        plt.plot(arr_t_list, Narrivals,  color='r', label = 'Number of arrival')
        plt.plot(arr_t_list, Ndepartures,  color='b', label = 'Number of departure')
        plt.plot(arr_t_list, ndroppacket,  color='y', label = 'Number of packet loss')
        plt.legend()
        plt.xlabel("arrival time [s]")
        plt.grid()
        plt.show()
