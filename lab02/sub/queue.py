
import random
import numpy as np
from queue import Queue, PriorityQueue
from sub.measurements import Measure
from sub.client import Client
from sub.server import Server

class Queue:
    def __init__(self, serv_t, arr_t, queue_len, n_server, event_names):
        """
        Queue
        ---
        Class used to model queuing systems.

        Input parameters:
        - serv_t: average service time (1/serv_rate)
        - arr_t: average inter-arrival time (1/arr_rate)
        - queue_len: maximum queue length (if None then infinite queue)
        - n_server: number of servers (if None then infinite queue)
        - servers: policy initialization
        - event_names: list containing 2 elements - 1st one is the name assigned to the arrivals, 
        2nd one is the one assigned to the departure

        Attributes:
        - TODO
        """

        self.serv_t = serv_t
        self.arr_t = arr_t
        self.queue_len = queue_len 
        self.n_server = n_server

        self.arr_name = event_names[0]
        self.dep_name = event_names[1]

        self.propagation_time = 0.2         # TODO: set proper value

        self.data = Measure(0,0,0,0,0,0, n_server)
        
        self.queue = []
        self.servers = Server(n_server, serv_t)
        
    
    def addClient(self, time, FES, event_type):
        """
        Decide whether the user can be added.
        Need to look at the QUEUE_LEN parameter.
        This subroutine is called by the 'arrival' method.
        """
        
        global users                # TODO: remove it
        
        #serv_id = event_type[1][1] ---> Removed - the Queue object needs to evaluate the next server

        pkt_type = event_type[1][1]
        if self.queue_len is not None:
            # Limited length
            if users < self.queue_len:
                users += 1
                self.data.n_usr_t.append((users, time))
                # create a record for the client
                client = Client(pkt_type,time)
                # insert the record in the queue
                self.queue.append(client)
                
                # If there are less clients than servers, it means that the 
                # new client can directly be served
                # It may also be that the number of servers is unlimited 
                # (new client always finds a server)
                if self.n_server is None or users<=self.n_server:
                    # Choose the next server
                    serv_id = self.servers.chooseNextServer()

                    # sample the service time
                    service_time, serv_id = self.servers.evalServTime(type="constant")
                    self.data.servicesList.append(service_time)
                    #service_time = 1 + random.uniform(0, SEVICE_TIME)

                    # schedule when the client will finish the server
                    FES.put((time + service_time, [self.dep_name]))
                    self.servers.makeBusy(serv_id)
                    
                    if self.n_server is not None:
                        # Update the beginning of the service
                        self.data.serv_busy[serv_id]['begin_last_service'] = time

                    # Update the waiting time for the client which starts to be served straight away
                    # Get the client - not extracting:
                    cli = self.queue[0]
                    self.data.waitingDelaysList.append(time - cli.arrival_time)

            else:
                # Lost client
                self.data.countLosses += 1
        else:
            # Unlimited length
            users += 1
            self.data.n_usr_t.append((users, time))

            # create a record for the client
            client = Client(pkt_type, time)

            # insert the record in the queue
            self.queue.append(client)

            # If there are less clients than servers, it means that the 
            # new client can directly be served
            if self.n_server is None or users<=self.n_server:

                # sample the service time
                service_time, serv_id = self.servers.evalServTime(type="constant")
                self.data.servicesList.append(service_time)
                #service_time = 1 + random.uniform(0, SEVICE_TIME)

                # schedule when the client will finish the server
                FES.put((time + service_time, [self.dep_name, serv_id]))
                self.servers.makeBusy(serv_id)

                if self.n_server is not None:
                    # Update the beginning of the service
                    self.data.serv_busy[serv_id]['begin_last_service'] = time
                
                # Update the waiting time for the client which starts to be served straight away
                # Get the client - not extracting:
                cli = self.queue[0]
                self.data.waitingDelaysList.append(time - cli.arrival_time)

    # arrivals *********************************************************************
    def arrival(self, time, FES, event_type):
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
        
        assert (len(self.queue) == users), "The len of the queue and number of clients don't match"

        #print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )
        
        # cumulate statistics
        self.data.arr += 1
        self.data.ut += users*(time-self.data.oldT)
        self.data.avgBuffer += max(0, users - self.n_server)*(time-self.data.oldT)
        self.data.oldT = time

        # sample the time until the next event
        inter_arrival = random.expovariate(lambd=1.0/self.arr_t)
        self.data.arrivalsList.append(inter_arrival)
        
        # schedule the next arrival
        FES.put((time + inter_arrival, [self.arr_name]))

        ################################
        self.addClient(time, FES, event_type)
        ################################

    # departures *******************************************************************
    def departure(self, time, FES, queue, event_type):
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
        serv_id = event_type[1][1]
        type_pkt = event_type[1][2]
        # cumulate statistics
        self.data.dep += 1
        self.data.ut += users*(time-self.data.oldT)
        self.data.avgBuffer += max(0, users - self.n_server)*(time-self.data.oldT)

        self.data.oldT = time
        
        if len(queue) > 0:
            # get the first element from the queue
            client = queue.pop(0)

            # Make its server idle
            self.servers.makeIdle(serv_id)

            if self.n_server is not None:
                # Update cumulative server busy time
                
                # Add to the cumulative time the time difference between now (service end)
                # and the beginning of the service
                # print(data.serv_busy[serv_id]['cumulative_time'])
                self.data.serv_busy[serv_id]['cumulative_time'] += (time - self.data.serv_busy[serv_id]['begin_last_service'])
            
            # do whatever we need to do when clients go away
            
            self.data.delay += (time-client.arrival_time)
            self.data.delaysList.append(time-client.arrival_time)
            users -= 1
            self.data.n_usr_t.append((users, time))
        
        # Update time
        self.data.oldT = time

        can_add = False

        # See whether there are more clients in the line
        if self.n_server is not None:
            if users >= self.n_server:
                can_add = True
        elif users > 0:
            can_add = True

        ########## SERVE ANOTHER CLIENT #############
        if can_add:
            # Sample the service time
            service_time, new_serv_id = self.servers.evalServTime(type="constant")
            self.data.servicesList.append(service_time)

            new_served = queue[0]

            self.data.waitingDelaysList.append(time-new_served.arrival_time)
            self.data.waitingDelaysList_no_zeros.append(time-new_served.arrival_time)

            # Schedule when the service will end
            FES.put((time + service_time, [self.dep_name, new_serv_id]))
            self.servers.makeBusy(new_serv_id)

            if self.n_server is not None:
                # Update the beginning of the service
                self.data.serv_busy[new_serv_id]['begin_last_service'] = time

        