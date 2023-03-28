import numpy as np

# ******************************************************************************
# Server
# ******************************************************************************
class Server(object):
    # constructor
    def __init__(self):
        # whether the server is idle or not
        self.idle = True