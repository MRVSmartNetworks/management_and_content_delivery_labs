import numpy as np
import random
import warnings

# ******************************************************************************
# Server
# ******************************************************************************
class Server(object):
    # constructor
    def __init__(self, n_serv, dep_rate, policy="first_idle"):
        """
        Class used to model servers in the queuing system. 

        Parameters:
        - n_serv: number of servers
        - dep_rate: service rate; if one single value it is the rate for all 
        servers, if it is a list, it contains the rates for each server (the 
        length must be n_serv)
        - policy: it is the policy for the choice of the server; default: 
        'first_idle'

        Attributes:
        - 
        """
        
        # Case n_serv = None: ???????

        self.n_servers = n_serv

        if n_serv is None:
            # Unlimited servers
            self.valid_policies = [
                "first_idle"            # Only policy for the infinite n. of servers - keep on adding... (cumbersome)
            ]

            # The service rate for the case of infinite servers is a list containing one single 
            # value (the index self.current will always stay the same)
            if isinstance(dep_rate, int) or isinstance(dep_rate, float):
                self.dep_rates = [dep_rate]
            elif isinstance(dep_rate, list) and len(dep_rate) == 1:
                self.dep_rates = dep_rate
            else:
                raise ValueError("The value for 'dep_rate' is wrong!")

        else:
            # Limited servers
            self.valid_policies = [
                "first_idle",           # The next client is served by the 1st idle server
                "round_robin"           # The assignment is done in a round robin fashion (the client is assigned to server 'i', the next one to server 'i+1')
            ]

            if isinstance(dep_rate, int) or isinstance(dep_rate, float):
                self.dep_rates = [dep_rate] * n_serv
            elif isinstance(dep_rate, list) and len(dep_rate) == n_serv:
                self.dep_rates = dep_rate
            else:
                raise ValueError("The value for 'dep_rate' is wrong!")

            # Check for correct policy
            if policy not in self.valid_policies:
                raise ValueError("Wrong policy specified!")
            else:
                self.policy = policy

            ################################################################################

            # Whether each server is idle or not - init all to True (all idle)
            self.idle = [True] * n_serv

        # 'current' is used to track the choice of the next server
        # NOTE: if the n. of servers is infinite, the number 'current' will always stay 0 
        # (it is instantiated for simplicity)
        self.current = 0

    # ******************************************************************************
    # Private

    def chooseNextServer(self):
        """
        Update the attribute 'current', which chooses the next server to be used

        NOTE: the program should already check for the possibility to add the client
        """

        if self.n_servers is not None:
            # count_loop = 0          # Used to track the attempts to find a free servers

            if self.policy == "first_idle":
                self.current = 0
                while not self.idle[self.current]:
                    self.current += 1
                    self.current = self.current % self.n_servers
            elif self.policy == "round_robin":
                self.current += 1
                self.current = self.current % self.n_servers
                while not self.idle[self.current]:
                    self.current += 1
                    self.current = self.current % self.n_servers
        else:
            # No need to keep counter if infinite n. of servers - leave it 0
            self.current = 0

    # ******************************************************************************
    # Public

    def evalServTime(self, type="expovariate"):
        """
        Generate an instance of the service time for the next server

        The method returns the value and the server id

        Parameters:
        - type: distribution type
        """
        # Update 
        self.chooseNextServer()

        if type == "expovariate":
            service_time = random.expovariate(1.0/self.dep_rates[self.current])
        else:
            raise ValueError(f"Invalid distribution type '{type}'!")
        
        return service_time, self.current
    
    def makeIdle(self, serv_id):
        """
        Change the state of server 'serv_id' from busy to idle.
        A warning is raised if the server was already idle (something is 
        wrong with the program calling this method).
        """

        if self.n_servers is not None and serv_id < self.n_servers:
            if self.idle[serv_id]:
                warnings.warn(f"The server {serv_id} was already idle!")

            self.idle[serv_id] = True
        elif self.n_servers is None:
            # No need to update - infinite n. of servers
            pass
        else:
            raise ValueError(f"The provided ID {serv_id} exceeds the maximum number of servers {self.n_servers}")



    def makeBusy(self, serv_id):
        """
        Change the state of server 'serv_id' from idle to busy.
        A warning is raised if the server was already busy (something is 
        wrong with the program calling this method).
        """
        if self.n_servers is not None and serv_id < self.n_servers:
            if not self.idle[serv_id]:
                warnings.warn(f"The server {serv_id} was already busy!")
            
            self.idle[serv_id] = False
        elif self.n_servers is None:
            # No need to update - infinite n. of servers
            pass
        else:
            raise ValueError(f"The provided ID {serv_id} exceeds the maximum number of servers {self.n_servers}")

