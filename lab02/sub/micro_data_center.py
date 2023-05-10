from sub.server import Server
from sub.client import Client

from sub.queue import Queue

import random

DEBUG = False


class MicroDataCenter(Queue):
    """
    MicroDataCenter
    ---
    Class used to model the Micro Data Center.
    It handles packets of types A and B, according to different policies:

    - Packets 'A' - High priority: time-sensitive tasks, which require to be executed
    at edge level; once they are processed by the M.D.C., these packets are
    immediately sent to the actuators.
    - Packets 'B' - Low priority: time-insentitive tasks, which have to go through
    both processing at Micro Data Center and at Cloud Data Center

    This class inherits all methods from the `Queue' class and overrides some of them.
    """

    def departure(self, time, FES, event_type):
        type_pkt = event_type[1]
        serv_id = event_type[2]
        # cumulate statistics
        self.data.dep += 1
        self.data.ut += self.users * (time - self.data.oldT)
        self.data.ut_in_time.append([time, self.data.ut])

        self.data.avgBuffer += max(0, self.users - self.n_server) * (
            time - self.data.oldT
        )

        self.data.oldT = time

        if len(self.queue) > 0:
            # get the first element from the self.queue
            client = self.queue.pop(0)

            if type_pkt == "B":
                FES.put((time + self.propagation_time, ["arrival_cloud", client.type]))
            else:
                # Going to actuator
                # print something?
                pass

            # Make its server idle
            self.servers.makeIdle(serv_id)
            if self.n_server is not None:
                # Update cumulative server busy time

                # Add to the cumulative time the time difference between now (service end)
                # and the beginning of the service
                # print(data.serv_busy['cumulative_time'])
                self.data.serv_busy[serv_id]["cumulative_time"] += (
                    time - self.data.serv_busy[serv_id]["begin_last_service"]
                )

            # do whatever we need to do when clients go away
            if client.type == "A":
                self.data.delay_A += time - client.arrival_time
                self.data.delay_pkt_A[client.pkt_ID] = time - client.arrival_times[-1]
            elif client.type == "B":
                self.data.delay_B += time - client.arrival_time
                self.data.delay_pkt_B[client.pkt_ID] = time - client.arrival_times[-1]

            self.data.delay += time - client.arrival_time
            self.data.delaysList.append(time - client.arrival_time)
            self.users -= 1
            self.data.n_usr_t.append((self.users, time))

        # Update time
        self.data.oldT = time

        can_add = False

        # See whether there are more clients in the line
        if self.n_server is not None:
            if self.users >= self.n_server:
                can_add = True
        elif self.users > 0:
            can_add = True

        ########## SERVE ANOTHER CLIENT #############
        if can_add:
            # Sample the service time
            service_time, new_serv_id = self.servers.evalServTime(type="expovariate")
            self.data.servicesList.append(service_time)

            new_served = self.queue[0]

            # Update total costs (they will be 0 if not defined)
            self.data.tot_serv_costs += self.servers.costs[new_serv_id]

            self.data.waitingDelaysList.append(time - new_served.arrival_time)
            self.data.waitingDelaysList_no_zeros.append(time - new_served.arrival_time)

            # Schedule when the service will end
            FES.put(
                (time + service_time, [self.dep_name, new_served.type, new_serv_id])
            )
            self.servers.makeBusy(new_serv_id)

            if self.n_server is not None:
                # Update the beginning of the service
                self.data.serv_busy[new_serv_id]["begin_last_service"] = time

    # No need to implement the method 'arrival' since we already changed 'addClient'
    # def arrival(self, time, FES, event_type):
    #     Queue.arrival()

    def addClient(self, time, FES, event_type):
        """
        addClient
        ---
        Decide whether it is possible to add the client to the
        queuing system.
        If not, forward it to the cloud data center.
        """
        # Need to specify policy for 'lost' packets!
        pkt_type = event_type[1]

        if self.queue_len is not None:
            # Limited length ------------- Only case for this lab

            if self.users < self.queue_len:
                self.users += 1
                self.data.n_usr_t.append((self.users, time))
                self.data.count_types[pkt_type] += 1

                new_pkt_id = f"{pkt_type}{self.data.count_types[pkt_type]}"

                ## Create a record for the client
                client = Client(pkt_type, time, new_pkt_id)
                # Add new arrival for the new client (used to evaluate the queuing delay at the end)
                client.addNewArrival(time)

                # insert the record in the self.queue
                self.queue.append(client)

                # If there are less clients than servers, it means that the
                # new client can directly be served
                # It may also be that the number of servers is unlimited
                # (new client always finds a server)
                if self.n_server is None or self.users <= self.n_server:
                    # sample the service time
                    service_time, serv_id = self.servers.evalServTime(
                        type="expovariate"
                    )
                    self.data.servicesList.append(service_time)
                    # service_time = 1 + random.uniform(0, SEVICE_TIME)

                    # schedule when the client will finish the server
                    FES.put(
                        (time + service_time, [self.dep_name, client.type, serv_id])
                    )
                    self.servers.makeBusy(serv_id)

                    # Update total costs (they will be 0 if not defined)
                    self.data.tot_serv_costs += self.servers.costs[serv_id]

                    if self.n_server is not None:
                        # Update the beginning of the service
                        self.data.serv_busy[serv_id]["begin_last_service"] = time

                    # Update the waiting time for the client which starts to be served straight away
                    # Get the client - not extracting:
                    cli = self.queue[0]
                    self.data.waitingDelaysList.append(time - cli.arrival_time)

            else:
                # Full self.queue - send the client directly to the cloud

                # 'countLosses' is used to count the packets which are directly forwarded to the cloud when the micro data center is full
                if pkt_type == "A":
                    self.data.countLosses_B += 1
                elif pkt_type == "B":
                    self.data.countLosses_B += 1

                self.data.countLosses += 1

                if DEBUG:
                    print("loss at micro - forward packet to cloud directly")

                # Scedule arrival into cloud data center
                # It will happen after a fixed propagation time
                arr_time_cloud = time + self.propagation_time
                FES.put((arr_time_cloud, ["arrival_cloud", pkt_type]))

        else:
            # Unlimited length
            self.users += 1
            self.data.n_usr_t.append((self.users, time))

            # create a record for the client
            client = Client(pkt_type, time)

            # insert the record in the self.queue
            self.queue.append(client)

            # If there are less clients than servers, it means that the
            # new client can directly be served
            if self.n_server is None or self.users <= self.n_server:
                # sample the service time
                service_time, serv_id = self.servers.evalServTime(type="expovariate")
                self.data.servicesList.append(service_time)
                # service_time = 1 + random.uniform(0, SEVICE_TIME)

                # schedule when the client will finish the server
                FES.put((time + service_time, [self.dep_name, client.type, serv_id]))
                self.servers.makeBusy(serv_id)

                if self.n_server is not None:
                    # Update the beginning of the service
                    self.data.serv_busy[serv_id]["begin_last_service"] = time

                # Update the waiting time for the client which starts to be served straight away
                # Get the client - not extracting:
                cli = self.queue[0]
                self.data.waitingDelaysList.append(time - cli.arrival_time)
