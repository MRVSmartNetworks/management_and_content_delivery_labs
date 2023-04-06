import numpy as np
import random
import warnings

# ******************************************************************************
# Server
# ******************************************************************************
class Server(object):
    # constructor
    def __init__(self, n_serv, serv_t, policy="first_idle"):
        """
        Class used to model servers in the queuing system. 

        Parameters:
        - n_serv: number of servers
        - serv_t: average service time; if one single value it is the value for all 
        servers, if it is a list, it contains the values for each server (the 
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
            if isinstance(serv_t, int) or isinstance(serv_t, float):
                self.serv_rates = [1./serv_t]
            elif isinstance(serv_t, list) and len(serv_t) == 1:
                self.serv_rates = [1./x for x in serv_t]
            else:
                raise ValueError("The value for 'serv_rate' is wrong!")

        else:
            # Limited servers
            self.valid_policies = [
                "first_idle",           # The next client is served by the 1st idle server
                "round_robin",           # The assignment is done in a round robin fashion (the client is assigned to server 'i', the next one to server 'i+1')
                "faster_first"
            ]

            if isinstance(serv_t, int) or isinstance(serv_t, float):
                self.serv_rates = [1./serv_t] * n_serv
            elif isinstance(serv_t, list) and len(serv_t) == n_serv:
                self.serv_rates = [1./x for x in serv_t]
            else:
                raise ValueError("The value for 'serv_rate' is wrong!")

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
                # The policy 'first_idle' starts to look for a free server from the 1st one onwards
                self.current = 0
                while not self.idle[self.current]:
                    self.current += 1
                    self.current = self.current % self.n_servers
            elif self.policy == "round_robin":
                # The policy 'round_robin' looks for a free server in an ordered way 
                self.current += 1
                self.current = self.current % self.n_servers
                while not self.idle[self.current]:
                    self.current += 1
                    self.current = self.current % self.n_servers
            elif self.policy == "faster_first":
                # Sort the service rates (decreasing order)
                sorted = np.argsort(-1*np.array(self.serv_rates))
                self.current = sorted[0]
                i = 1
                while not self.idle[self.current]:
                    self.current = sorted[i]
                    i += 1
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
            -> Possible values: 
            > expovariate: exponential service time
            > constant: constant service time equal to 1/serv_rate of current server
            > uniform: uniform in (0, 2/serv_rate) of current server
        """
        # Update 
        self.chooseNextServer()

        if type == "expovariate":
            service_time = random.expovariate(self.serv_rates[self.current])
        elif type == "constant":
            service_time = 1./self.serv_rates[self.current]
        elif type == "uniform":
            service_time = (2./self.serv_rates[self.current])*random.uniform()
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

