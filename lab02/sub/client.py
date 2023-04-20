import numpy as np

# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self,type,arrival_time):
        """
        Client

        Client objects are used to model packets in a queuing system
        """
        self.type = type
        self.arrival_time = arrival_time