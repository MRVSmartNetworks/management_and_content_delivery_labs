import numpy as np


# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self, type, arrival_time, id=""):
        """
        Client

        Client objects are used to model packets in a queuing system
        """
        self.type = type
        self.arrival_time = arrival_time
        # Unique ID of the packets - the format is "[type][Number]", e.g., "A10"
        self.pkt_ID = id

        self.arrival_times = []

    def addNewArrival(self, time):
        self.arrival_times.append(time)
