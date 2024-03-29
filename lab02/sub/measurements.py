import matplotlib.pyplot as plt
import numpy as np


class Measure:
    def __init__(
        self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay, countLoss, n_servers
    ):
        """ """

        self.n_serv = n_servers

        # Keep a count for the number of packets of each type
        # NOTE: this is the number of packets which ENTER the queue
        self.count_types = {"A": 0, "B": 0}

        self.arr = Narr  # Count arrivals (also including lost packets)
        self.dep = Ndep  # Count departures (TRANSMITTED PACKETS)
        # Count average number of users in time - add to ut the number of clients times the time span it remained constant
        self.ut = NAveraegUser  # N packets * dt
        self.ut_in_time = []

        self.n_usr_t = [
            (0, 0)
        ]  # Number of users in time, append tuple (n_user, current time) at each measurement
        self.oldT = OldTimeEvent  # Time of the last performed event
        self.delay = AverageDelay  # Average time spent in system
        self.delay_A = 0  # Average time spent by packet A in system
        self.delay_B = 0  # Average time spent by packet B in system

        self.countLosses = countLoss  # Number of losses (DROPPED PACKETS)
        self.countLosses_t = [(0,0)]    #Number of losses in time; tuple (no. losses, current time)
        self.countLosses_A = countLoss
        self.countLosses_B = countLoss

        # Delay of packets A - This dict has as keys the packet IDs and as values the evaluated delays for the queue
        self.delay_pkt_A = {}
        # Delay of packets B
        self.delay_pkt_B = {}

        # Distribution of the queuing delay
        # Save all values as a list and make the histogram when needed
        self.delaysList = []

        # Store all inter arrival times:
        self.arrivalsList = []

        # Store all service times
        self.servicesList = []

        # AVERAGE WAITING DELAY PER PACKET
        # Evaluated between the arrival in the system and the start of the service
        # for each client
        self.waitingDelaysList = (
            []
        )  # Considering all clients which successfully entered system (not dropped)
        self.waitingDelaysList_no_zeros = (
            []
        )  # Without considering the ones that have been directy been served
        # Also store the time at which the measurements were saved
        # This is used for the evaluation of the transient
        self.waiting_delays_times = []

        self.avgBuffer = 0  # Average Buffer Occupancy - time average
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

            self.serv_busy = [
                {"cumulative_time": 0, "begin_last_service": 0}
                for i in range(n_servers)
            ]
        else:
            # Unlimited n. of servers       ! complicated
            pass

        ### Total operation cost:
        self.tot_serv_costs = 0

    def queuingDelayHist(self, mean_value=False, img_name=None):
        """
        Plot the histogram of the queuing delay values

        Parameters:
        - mean_value: if true, plot the vertical line corresponding to the mean value of
        the queuing delay
        - img_name: if provided (not None) the plot will be saved in the provided location
        """
        plt.figure(figsize=(8, 4))
        plt.hist(self.delaysList, bins=round(np.sqrt(len(np.unique(self.delaysList)))))
        if mean_value:
            # Plot the horizontal line corresponding to the mean
            plt.axvline(
                np.mean(self.delaysList), color="k", linestyle="dashed", linewidth=1
            )
        plt.title("Queuing delay histogram")
        plt.xlabel("Delay")
        plt.ylabel("# in bins")
        plt.grid()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)
        plt.show()

    def plotQueuingDelays(self, img_name=None):
        """
        Plot the values of the queuing delays in the order they have been
        added in the list (i.e., in time).

        Parameters:
        - img_name: if provided, save the plot in the specified location
        """
        plt.figure(figsize=(8, 4))
        plt.plot(list(range(len(self.delaysList))), self.delaysList)
        plt.title("Values of the queuing delay in time")
        plt.grid()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)
        plt.show()

    def plotServUtilDelay(self, sim_time, policy=None, img_name=None):
        """
        Plot a histogram containing for each server the utilization.

        Parameters:
        - sim_time: value of the simulation time (needed for performing the normalization)
        - policy: string containing the used policy for assigning server
        - img_name: if provided, save the plot in the specified location
        """
        # Divide the time by the total simulation time to get the utilization
        if self.n_serv is not None:
            fig = plt.figure(figsize=(8, 4))
            plt.bar(
                list(range(1, self.n_serv + 1)),
                [x["cumulative_time"] / sim_time for x in self.serv_busy],
                width=0.4,
            )
            plt.xlabel("Server ID")
            plt.ylabel("Utilization")
            if policy is None:
                plt.title(f"Server utilization")
            elif isinstance(policy, str):
                plt.title(f"Server policy: {policy}")
                if img_name is not None:
                    img_name = img_name.split(".")[0] + f"_{policy}" + ".png"
            plt.tight_layout()
            if img_name is not None:
                plt.savefig(img_name, dpi=300)
            plt.show()
        else:
            print("Unable to print utilization of servers - they are unlimited")

    def plotUsrInTime(self, mean_value=False, img_name=None):
        """
        Plot the number of users in time.

        Parameters:
        - img_name: if provided, save the plot in the specified location
        """
        plt.figure(figsize=(12, 5))
        plt.plot([t[1] for t in self.n_usr_t], [t[0] for t in self.n_usr_t])
        if mean_value:
            plt.hlines(
                np.mean([t[0] for t in self.n_usr_t]),
                0,
                self.n_usr_t[-1][1],
                "r",
                linestyles="dashed",
            )
            plt.title("Number of users in time (with mean value)")
        else:
            plt.title("Number of users in time")
        plt.xlabel("time")
        plt.ylabel("# packets")
        plt.grid()
        plt.tight_layout()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)

        plt.show()

    def plotUsrMovingAvg(self, img_name=None):
        """
        Plot the (time) average of the users in time, i.e., (n_users * dt) / time
        """
        plt.figure(figsize=(12, 5))
        plt.plot(
            [v[0] for v in self.ut_in_time[1:]],
            [v[1] / v[0] for v in self.ut_in_time[1:]],
        )
        plt.title("Moving average of the number of packets in the queue")
        plt.grid()
        plt.xlabel("Time")
        plt.ylabel("Time avg. users")
        plt.tight_layout()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)
        plt.show()

    def plotArrivalsHist(self, mean_value=False, img_name=None):
        """
        Plot the distribution of the arrival rates.

        Parameters:
        - mean_value: if True, plot a vertical line corresponding to the experimental mean value
        - img_name: if provided, save the plot in the specified location
        """
        plt.figure(figsize=(8, 4))
        plt.hist(
            self.arrivalsList, bins=round(np.sqrt(len(np.unique(self.arrivalsList))))
        )
        if mean_value:
            plt.axvline(
                np.mean(self.arrivalsList), color="k", linestyle="dashed", linewidth=1
            )
        plt.xlabel("Inter-arrival time values")
        plt.ylabel("# in bin")
        plt.title("Inter-arrival time distribution")
        plt.grid()
        plt.tight_layout()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)
        plt.show()

    def plotServiceTimeHist(self, mean_value=False, img_name=None):
        """
        Plot the service time distribution.

        Parameters:
        - mean_value: if True, plot a vertical line corresponding to the experimental mean value
        - img_name: if provided, save the plot in the specified location
        """
        plt.figure(figsize=(8, 4))
        plt.hist(
            self.servicesList, bins=round(np.sqrt(len(np.unique(self.servicesList))))
        )
        if mean_value:
            plt.axvline(
                np.mean(self.servicesList), color="k", linestyle="dashed", linewidth=1
            )
        plt.xlabel("service time values")
        plt.ylabel("# in bin")
        plt.title("Service time distribution")
        plt.grid()
        plt.tight_layout()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)
        plt.show()

    def waitingDelayHist(self, zeros=False, mean_value=False, img_name=None):
        """
        waitingDelayHist
        ---
        Plot the histogram of the queuing delay values.

        Parameters:
        - zeros: if true, plot the distribution taking into account elements which do
        not wait before service, else, don't
        - mean_value: if true, plot the vertical line corresponding to the mean value of
        the waiting delay
        - img_name: if provided (not None) the plot will be saved in the provided location
        """
        plt.figure(figsize=(8, 4))
        if zeros:
            plt.hist(
                self.waitingDelaysList,
                bins=round(np.sqrt(len(np.unique(self.waitingDelaysList)))),
            )
            if mean_value:
                # Plot the horizontal line corresponding to the mean
                plt.axvline(
                    np.mean(self.waitingDelaysList),
                    color="k",
                    linestyle="dashed",
                    linewidth=1,
                )
            plt.title("Waiting delay histogram")
        else:
            plt.hist(
                self.waitingDelaysList_no_zeros,
                bins=round(np.sqrt(len(np.unique(self.waitingDelaysList_no_zeros)))),
            )
            if mean_value:
                # Plot the horizontal line corresponding to the mean
                plt.axvline(
                    np.mean(self.waitingDelaysList_no_zeros),
                    color="k",
                    linestyle="dashed",
                    linewidth=1,
                )
            plt.title("Waiting delay histogram - no zeros considered")
        plt.xlabel("Delay")
        plt.ylabel("# in bins")
        # plt.grid()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)
        plt.show()

    def waitingDelayInTime(self, mean_value=False, img_name=None):
        """
        waitingDelayInTime
        ---
        Plot the values of the waiting delay in time.

        ### Input parameters:
        - img_name: if provided (not None) the plot will be saved in the provided location
        """

        plt.figure(figsize=(8, 4))
        plt.plot(self.waitingDelaysList, "b")
        if mean_value:
            plt.hlines(
                np.mean(self.waitingDelaysList),
                0,
                len(self.waitingDelaysList),
                "r",
                linestyles="dashed",
            )
            plt.title("Waiting delay evolution in time (with mean value)")
        else:
            plt.title("Waiting delay evolution in time")
        plt.xlabel("Client number")
        plt.ylabel("Waiting delay")
        plt.tight_layout()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)
        plt.show()

    def avgWaitDelayInTime(self, figsize=(10, 5), img_name=None):
        """
        avgWaitDelayInTime
        ---
        Plot the moving average of the waiting delay in time.
        This plot can be used to observe the initial transient.

        ### Input parameters
        - img_name (default None): if not None, save the produced image
        at the specified path.
        """
        plt.figure(figsize=figsize)
        plt.plot(
            self.waiting_delays_times[1:],
            [
                sum(self.waitingDelaysList[:i]) / (i)
                for i in range(1, len(self.waitingDelaysList))
            ],
        )
        plt.title("Average of the waiting delay in time")
        plt.xlabel("time")
        plt.ylabel("Average waiting delay")
        plt.grid()
        plt.tight_layout()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)
        plt.show()

    def plotLossesInTime(self, mean_value=False, img_name=None):
        """
        Plot the number of losses in time.

        Parameters:
        - img_name: if provided, save the plot in the specified location
        """
        plt.figure(figsize=(12, 5))
        plt.plot([t[1] for t in self.countLosses_t], [t[0] for t in self.countLosses_t])
        if mean_value:
            plt.hlines(
                np.mean([t[0] for t in self.countLosses_t]),
                0,
                self.countLosses_t[-1][1],
                "r",
                linestyles="dashed",
            )
            plt.title("Number of losses in time (with mean value)")
        else:
            plt.title("Number of losses in time")
        plt.xlabel("time")
        plt.ylabel("# losses")
        plt.grid()
        plt.tight_layout()
        if img_name is not None:
            plt.savefig(img_name, dpi=300)

        plt.show()