import matplotlib.pyplot as plt
import numpy as np

class Measure:
    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay, countLoss, n_servers):
        """  """

        self.n_serv = n_servers

        self.arr = Narr                         # Count arrivals (also including lost packets)
        self.dep = Ndep                         # Count departures (TRANSMITTED PACKETS)
        # Count average number of users in time - add to ut the number of clients times the time span it remained constant
        self.ut = NAveraegUser                  # N packets * dt
        self.n_usr_t = [(0,0)]                  # Number of users in time, append tuple (n_user, current time) at each measurement
        self.oldT = OldTimeEvent                # Time of the last performed event
        self.delay = AverageDelay               # Average time spent in system
        #
        self.countLosses = countLoss            # Number of losses (DROPPED PACKETS)

        # Distribution of the queuing delay
        # Save all values as a list and make the histogram when needed
        self.delaysList = []

        # AVERAGE WAITING DELAY PER PACKET
        # Evaluated between the arrival in the system and the start of the service
        # for each client
        self.waitingDelaysList = []             # Considering all clients which successfully entered system (not dropped)
        self.waitingDelaysList_no_zeros = []    # Without considering the ones that have been directy been served

        self.avgBuffer = 0      # Average Buffer Occupancy - time average
        # Increased by max(0, n_users - n_servers)*dt each time

        # Loss probability (n. lost/n. arrivals)
        # Simply obtained by dividing the number of losses by the total n. of arrivals

        # Busy time - time spent in non-idle state (for each server) - if many servers
        # Idea: update server class, plus add new required parameter in this class (n_servers)
        # Question: how to deal with multiple servers? Which of the many is occupied?
        if n_servers is not None:
            # The attribute 'serv_busy' is a list with as many elements as the n. of servers
            # It contains the cumulative service time for each server and the beginning of 
            # the last service.

            self.serv_busy = [{'cumulative_time': 0, 'begin_last_service': 0} for i in range(n_servers)]
        else:
            # Unlimited n. of servers       ! complicated
            pass

        

    def queuingDelayHist(self, mean_value=None, img_name=None):
        """
        Plot the histogram of the queuing delay values
        """
        plt.hist(self.delaysList, bins=round(np.sqrt(len(np.unique(self.delaysList)))))
        if mean_value is not None:
            # Plot the horizontal line corresponding to the mean
            plt.hlines(y=mean_value, xmin=min(self.delaysList), xmax=max(self.delaysList))
        plt.title("Queuing delay histogram")
        plt.xlabel("Delay")
        plt.xlabel("N. in bins")
        plt.grid()
        if img_name is not None:
            plt.savefig(img_name)
        plt.show()

    def plotQueuingDelays(self, img_name=None):
        """
        Plot the values of the queuing delays in the order they have been 
        added in the list (i.e., in time).
        """

        plt.plot(list(range(len(self.delaysList))), self.delaysList)
        plt.title("Values of the queuing delay in time")
        plt.grid()
        if img_name is not None:
            plt.savefig(img_name)
        plt.show()

    def plotServUtilDelay(self, sim_time, policy=None, img_name=None):
        """
        Plot a histogram containing for each server the utilization.
        """
        # Divide the time by the total simulation time to get the utilization
        if self.n_serv is not None:
            fig = plt.figure(figsize=(8, 4))
            plt.bar(list(range(1, self.n_serv + 1)), [x['cumulative_time']/sim_time for x in self.serv_busy], width=0.4)
            plt.xlabel("Server ID")
            plt.ylabel("Utilization")
            if policy is None:
                plt.title(f"Server utilization")
            elif isinstance(policy, str):
                plt.title(f"Server policy: {policy}")
                if img_name is not None:
                    img_name = img_name.split('.')[0] + f"_{policy}" + ".png"
            plt.tight_layout()
            if img_name is not None:
                plt.savefig(img_name)
            
            plt.show()
        else:
            print("Unable to print utilization of servers - they are unlimited")

    def plotUsrInTime(self, img_name=None):
        plt.figure(figsize=(12,5))
        plt.plot([t[1] for t in self.n_usr_t], [t[0] for t in self.n_usr_t])
        plt.title("Number of users in time")
        plt.xlabel("time")
        plt.ylabel("# packets")
        plt.grid()
        plt.tight_layout()
        if img_name is not None:
                plt.savefig(img_name)
        
        plt.show()