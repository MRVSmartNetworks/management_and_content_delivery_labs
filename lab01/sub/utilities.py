import matplotlib.pyplot as plt 
import numpy as np

def printResults(n_server, queue_len, arr_t, serv_t, users, data, time, MM_system, SIM_TIME):
        print("******************************************************************************")

        print("SYSTEM PARAMETERS:\n")
        print(f"Number of servers: {n_server}\nMaximum queue length: {queue_len}")
        print(f"Packet arrival rate: {1./arr_t}\nService rate: {1./serv_t}")

        print(f"\nSimulation time: {SIM_TIME}")

        print("******************************************************************************")
        print("MEASUREMENTS: \n\nNo. of users in the queue (at stop): ",users,"\nNo. of total arrivals =",
            data.arr,"- No. of total departures =",data.dep)
         
        print("Load: ",serv_t/arr_t)
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

        data.queuingDelayHist()
        data.plotQueuingDelays()
        data.plotServUtilDelay(sim_time=SIM_TIME, policy="round_robin")


def plotArrivalRate(arr_t_list, data_list, param):
        """  
        - arr_t_list: list of arrival rates on x-axis
        - data_list: list of object data to get desired metrics
        - param
            - param[0]: queue lenght
            - param[1]: number of servers
            - param[2]: service time
        """
        # plots for number of packets
        plt.figure()
        plt.title(f"Packets on different arrival rates - queue_len = {param[0]} - n_server = {param[1]} - serv_r= {1./param[2]}")
        plt.plot([1./x for x in arr_t_list], [data.arr for data in data_list],  color='r', label = 'Number of arrival')
        plt.plot([1./x for x in arr_t_list], [data.dep for data in data_list],  color='b', label = 'Number of departure')
        plt.plot([1./x for x in arr_t_list], [data.countLosses for data in data_list],  color='y', label = 'Number of packet loss')
        plt.legend()
        plt.xlabel("arrival rate [1/s]")
        plt.ylabel("no. of packets")
        plt.grid()

        # Average delay plots
        plt.figure()
        plt.title(f'Average delay - queue_len = {param[0]} - n_server = {param[1]} - serv_r= {1./param[2]}')
        plt.plot([1./x for x in arr_t_list], [np.average(data.waitingDelaysList_no_zeros) for data in data_list], label='Average waiting delay (only waiting)')
        plt.plot([1./x for x in arr_t_list], [np.average(data.waitingDelaysList) for data in data_list], label='Average waiting delay')
        plt.plot([1./x for x in arr_t_list], [data.delay/data.dep for data in data_list], label='Average delay')
        plt.legend()
        plt.ylabel("waiting delay [s]")
        plt.xlabel("arrival rate [1/s]")
        plt.grid()
        plt.show()

def plotQueueLen(queue_len_list, data_list, param):
        """  
        - queue_len_list: list of queue length on x-axis
        - data_list: list of object data to get desired metrics
        - param
            - param[0]: arrival time
            - param[1]: number of servers
            - param[2]: service time
        """
        # plots for number of packets
        plt.figure()
        plt.title(f"Packets on different arrival rates - arr_r = {1./param[0]} - n_server = {param[1]} - serv_r= {1./param[2]}")
        plt.plot(queue_len_list, [data.arr for data in data_list],  color='r', label = 'Number of arrival')
        plt.plot(queue_len_list, [data.dep for data in data_list],  color='b', label = 'Number of departure')
        plt.plot(queue_len_list, [data.countLosses for data in data_list],  color='y', label = 'Number of packet loss')
        plt.legend()
        plt.xlabel("queue length")
        plt.ylabel("no. of packets")
        plt.grid()

        # Average delay plots
        plt.figure()
        plt.title(f'Average delay - arr_r = {1./param[0]} - n_server = {param[1]} - serv_r= {1./param[2]}')
        plt.plot(queue_len_list, [np.average(data.waitingDelaysList_no_zeros) for data in data_list], label='Average waiting delay (only waiting)')
        plt.plot(queue_len_list, [np.average(data.waitingDelaysList) for data in data_list], label='Average waiting delay')
        plt.plot(queue_len_list, [data.delay/data.dep for data in data_list], label='Average delay')
        plt.legend()
        plt.ylabel("queue length")
        plt.xlabel("arrival rate [1/s]")
        plt.grid()
        plt.show()