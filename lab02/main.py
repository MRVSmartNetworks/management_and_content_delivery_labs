from sub.micro_data_center import MicroDataCenter
from sub.cloud_data_center import CloudDataCenter
import random
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from queue import Queue, PriorityQueue
import time as tm

DEBUG = False

basicRun = False
task_1 = False
task_2 = False
task_3 = False
task_4 = True
task_4a = True
task_4b = False
task_4c = False
task_4d = False

T_q = 50  # thresh of maximum average queuing time for pkt A

"""
Version:
              .o.       
             .888.      
            .8"888.     
           .8' `888.    
          .88ooo8888.   
         .8'     `888.  
        o88o     o8888o 
"""

"""
Procedure:
- Initialize objects of classes MicroDataCenter and CloudDataCenter
- Initialize FES
- Run main loop having set the simulation time

Keep in mind:
- Different arrivals and departures depending on the data center
  - arrival_micro -> arrival in micro data center, arrival_cloud -> arrival in cloud data center
  - (& same for departures)

ARRIVALS:
- Parameters ('event_type[1]'):
  - Name
  - Type of client

DEPARTURES:
- Parameters ('event_type[1]'):
  - Name
  - Server ID (for the server that will process packet)

"""


def printResults(sim_time, mdc, cdc, plots=False):
    """
    printResults
    ---
    Used to read and display the measurements done during the simulation.

    This function extracts the measures from the 'data' attributes of the
    2 queues.

    ### Input parameters
    - sim_time: total simulation time
    - mdc: 'MicroDataCenter' class object
    - cdc: 'CloudDataCenter' class object
    - plots: bool to choose whether to display figures (plots) or not
    """
    # Task 1(version A). Analysis of the waiting delay
    if task_1:
        cdc.data.waitingDelayHist(
            zeros=True,
            mean_value=True,
            img_name="images/task1_wait_delays_hist_cdc.png",
        )

        ## Plot moving average of the waiting delay (CDC only)
        cdc.data.avgWaitDelayInTime(img_name="images/task1_average_wait_cdc.png")

        avg_wait_del_time = [
            sum(cdc.data.waitingDelaysList[:i]) / (i)
            for i in range(1, len(cdc.data.waitingDelaysList))
        ]

        ### Removing warm-up transient
        # Evaluate mean of waiting delay and then find point in which relative variation becomes low
        avg_wait_del = np.mean(cdc.data.waitingDelaysList)

        avg_time_avg_wait_del = np.mean(avg_wait_del_time)

        # Evaluate the mean having removed the first 'k' samples
        avg_wait_rem_samples = [
            sum(avg_wait_del_time[i:]) / (len(avg_wait_del_time) - i)
            for i in range(1, len(avg_wait_del_time))
        ]

        relative_distance = (avg_wait_del_time - avg_wait_del) / avg_wait_del

        relative_variation = avg_wait_rem_samples - avg_time_avg_wait_del

        # Extract the index at which the relative distance is below the specified value (and never gets above again)
        precision_ss = 0.1
        indices_invalid = np.argwhere(abs(relative_distance) >= precision_ss)

        time_instant = max(indices_invalid)[0] + 1

        # The value present in 'time_instant' is the index to be used to find the actual
        # value of the time instant with the list 'waiting_delays_times'
        end_of_transient_time = cdc.data.waiting_delays_times[time_instant]

        if plots:
            plt.figure(figsize=(10, 5))
            plt.plot(
                cdc.data.waiting_delays_times[1:],
                relative_distance,
                "b",
                label="Relative variation",
            )
            # plt.hlines(
            #     avg_time_avg_wait_del,
            #     0,
            #     len(relative_variation),
            #     label="Mean value over whole simulation",
            # )
            plt.axvline(
                end_of_transient_time,
                linewidth=0.5,
                color="r",
                label="End of initial transient",
            )
            plt.title(
                f"Relative variation, average waiting delay - transient at {precision_ss * 100}%"
            )
            plt.grid()
            plt.xlabel("time")
            plt.ylabel("R")
            plt.legend()
            plt.tight_layout()
            plt.savefig("images/task1_transient_location.png", dpi=300)
            plt.show()

            cdc.data.plotUsrInTime()
            cdc.data.plotUsrMovingAvg()

        print(f"The initial transient ends at time t = {end_of_transient_time}")

    if DEBUG:
        print(
            f"Losses, mdc: {mdc.data.countLosses}\nLosses, cdc: {cdc.data.countLosses}"
        )
        print(f"Perceived inter arrival rate, cdc: {cdc.data.arr/sim_time}")
        print(f"Perceived inter arrival time, cdc: {sim_time/cdc.data.arr}")
        print(f"Average number of users, MDC: {mdc.data.ut/sim_time}")
        print(f"Average number of users, CDC: {cdc.data.ut/sim_time}")
        print()

    ##### Results about point 4
    if task_4:
        if task_4a:
            # mdc.data.plotLossesMovingAvg()
            # cdc.data.plotLossesMovingAvg()
            mdc.data.plotLossesInTime(img_name="lab02/images/mdc_lossTime.png")
            cdc.data.plotLossesInTime(img_name="lab02/images/cdc_lossTime.png")

            mdc.data.plotUsrInTime(
                mean_value=True, img_name="lab02/images/mdc_usrTime.png"
            )
            cdc.data.plotUsrInTime(
                mean_value=True, img_name="lab02/images/cdc_usrTime.png"
            )
        if task_4b:
            print(
                f"\nWHOLE SYSTEM\n",
                f"Queuing delay: {cdc.data.delay + mdc.data.delay}\n",
                "Packet drop probability:",
                f"{(cdc.data.countLosses + mdc.data.countLosses)/(cdc.data.arr + mdc.data.arr)}\n",
                f"Overall operational cost: {cdc.data.tot_serv_costs + mdc.data.tot_serv_costs}\n"
                "\nCLOUD DATA CENTER\n",
                f"Queuing delay: {cdc.data.delay}\n",
                f"Packet drop probability: {cdc.data.countLosses/cdc.data.arr}\n",
                f"Cloud servers total costs: {cdc.data.tot_serv_costs}\n",
                "\nMICRO DATA CENTER\n",
                f"Queuing delay: {mdc.data.delay}\n",
                f"Packet drop probability: {mdc.data.countLosses/mdc.data.arr}\n",
                f"Edge nodes total costs: {mdc.data.tot_serv_costs}",
            )
        # 4.c - Total cost
        if task_4c or task_4d:
            print("\n+---------------------------+")

            print(
                f"Total operational cost: {mdc.data.tot_serv_costs + cdc.data.tot_serv_costs}"
            )
            print(f"  - Total cost, MDC: {mdc.data.tot_serv_costs}")
            print(f"  - Total cost, CDC: {cdc.data.tot_serv_costs}")

            # 4.c - maximum queuing delay, packets A
            total_queuing_delays_A = {}
            for id in mdc.data.delay_pkt_A.keys():
                if id in cdc.data.delay_pkt_A:
                    total_queuing_delays_A[id] = (
                        mdc.data.delay_pkt_A[id] + cdc.data.delay_pkt_A[id]
                    )
                else:
                    total_queuing_delays_A[id] = mdc.data.delay_pkt_A[id]

            max_queuing_delay_A = max(total_queuing_delays_A.values())

        print(f"Maximum queuing delay, packets A: {max_queuing_delay_A}")
        print(
            f"Loss probability, packets A: {(cdc.data.countLosses_A +mdc.data.countLosses_A)/(cdc.data.arr + mdc.data.arr) }"
        )

        total_queuing_delays_B = {}
        for id in mdc.data.delay_pkt_B.keys():
            if id in cdc.data.delay_pkt_B:
                total_queuing_delays_B[id] = (
                    mdc.data.delay_pkt_B[id] + cdc.data.delay_pkt_B[id]
                )
            else:
                total_queuing_delays_B[id] = mdc.data.delay_pkt_B[id]

        max_queuing_delay_B = max(total_queuing_delays_B.values())

        print(f"Maximum queuing delay, packets B: {max_queuing_delay_B}")
        print(
            f"Loss probability, packets B: {(cdc.data.countLosses_B +mdc.data.countLosses_B)/(cdc.data.arr + mdc.data.arr) }"
        )

    return mdc.data, cdc.data


def run(
    sim_time,
    fract,
    arr_t=10.0,
    serv_t_1=3.0,
    q1_len=10,
    n_serv_1=1,
    serv_t_2=5.0,
    q2_len=20,
    n_serv_2=1,
    server_costs=False,
    results=False,
    plots=False,
):
    """
    Run
    ---
    Launch simulation of the queuing system, lab 2.

    ### Paramaters

    - sim_time: simulation time
    - fract: fraction of packets of type B
    - arr_t: average inter-arrival time, queue 1
    - serv_t_1: average service time, queue 1
    - q1_len: length of queue 1
    - n_serv_1: number of servers, queue 1
    - serv_t_1: average service time, queue 2
    - q2_len: length of queue 2
    - n_serv_2: number of servers, queue 2
    - results: bool to choose whether to print the results (stdout) or not
    - plots: bool to choose whether to display the plots or not
    """
    FES = PriorityQueue()

    # control if there are more service rate during the simulation
    # and split the simulation proportionally to the no. of service
    # rates

    MDC = MicroDataCenter(
        serv_t=serv_t_1,
        arr_t=arr_t,
        queue_len=q1_len,
        n_server=n_serv_1,
        event_names=["arrival_micro", "departure_micro"],
        costs=server_costs,
        fract=fract,
        in_transient=True,
    )

    CDC = CloudDataCenter(
        serv_t=serv_t_2,
        arr_t=arr_t,
        queue_len=q2_len,
        n_server=n_serv_2,
        event_names=["arrival_cloud", "departure_cloud"],
        costs=server_costs,
        fract=fract,
        in_transient=True,
    )

    # Pick at random the first packet given the fraction of B
    type_pkt = MDC.rand_pkt_type(fract)

    # Simulation time
    if isinstance(arr_t, list):
        step_time = sim_time / len(arr_t)
        step_app = step_time
        i = 0
        MDC.arr_t = arr_t[i]
    else:
        step_time = sim_time

    time = 0

    FES.put((0, ["arrival_micro", type_pkt, 0]))

    while time < step_time:
        # a = tm.time()
        (time, event_type) = FES.get()
        # b = tm.time()
        # print(f"Time to extract last: {b-a}")
        # print(f"Current time: {time} - event: {event_type}")

        # tm.sleep(2)

        if event_type[0] == "arrival_micro":
            MDC.arrival(time, FES, event_type)

        elif event_type[0] == "arrival_cloud":
            CDC.arrival(time, FES, event_type)

        elif event_type[0] == "departure_micro":
            MDC.departure(time, FES, event_type)

        elif event_type[0] == "departure_cloud":
            CDC.departure(time, FES, event_type)

        if (
            time > step_time and step_time < sim_time
        ):  # check if the simulation is not finished
            step_time += step_app
            i += 1
            MDC.arr_t = arr_t[i]

    # Might be used later for returning the results in multi-run simulations
    if plots:
        return printResults(sim_time, MDC, CDC, plots=True)
    elif results:
        return printResults(sim_time, MDC, CDC, plots=False)
    else:
        return 0


##################################################################

if __name__ == "__main__":
    random.seed(1)
    sim_time = 500000
    initial_transient_upper_bound = 2000
    fract = 0.5

    if basicRun:
        run(
            sim_time,
            fract,
            arr_t=3.0,
            serv_t_1=2.0,
            q1_len=10,
            serv_t_2=4.0,
            q2_len=20,
            results=True,
            plots=True,
        )

    ##############################################################

    ################ Task 1. Anlysis of CDC
    if task_1:
        print("+------------------ Task 1 ------------------+")
        run(
            sim_time,
            fract=fract,
            arr_t=2.0,
            serv_t_1=3,
            q1_len=10,
            serv_t_2=6.0,
            q2_len=20,
            results=True,
            plots=True,
        )

    ################ Task 2. Impact of micro data center queue length on the performance
    if task_2:
        print("+------------------ Task 2 ------------------+")
        # Iterations
        arr_t = 3.0
        n_iter = 15
        seeds = random.sample(range(1, 10 * n_iter), n_iter)

        q_lengths = [1, 2, 4, 5, 8, 10, 12, 15, 18, 20, 25]
        f_values = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1]

        tmp_res_a = []
        tmp_res_b = []
        tmp_res_c = []

        ################# a. Changing the queue length, MDC
        print("2a --------------------")
        for i in range(len(q_lengths)):
            DEBUG = True
            random.seed(seeds[i])
            tmp_res_a.append(
                run(
                    sim_time,
                    fract,
                    serv_t_1=10.0,
                    q1_len=q_lengths[i],
                    serv_t_2=15.0,
                    q2_len=20,
                    results=True,
                )
            )

        ## Plot results:
        # Avg. users in queue 1 (MDC)
        avg_usr_mdc_a = [x[0].ut / sim_time for x in tmp_res_a]

        # Avg. users in queue 2
        avg_usr_cdc_a = [x[1].ut / sim_time for x in tmp_res_a]

        plt.figure(figsize=(10, 5))
        plt.plot(q_lengths, avg_usr_mdc_a, "b", label="Micro Data Center")
        plt.plot(q_lengths, avg_usr_cdc_a, "r", label="Cloud Data Center")
        plt.legend()
        plt.grid()
        plt.title("Average number of users in both queues vs. queue 1 (MDC) size")
        plt.xlabel("Queue 1 length")
        plt.ylabel("Avg. users")
        plt.tight_layout()
        plt.savefig("./images/task2_avg_n_q1_len.png")
        plt.show()

        # Losses

        """
        Comments: having fixed the values of the service times so that the situation is 
        'critical', it is possible to observe how the cloud data center experiences the
        impact of smaller queue sizes at the mdc by becoming overwhelmed, while, when 
        the queue size of the mdc gets bigger, the cdc does not need to absorb as many 
        of the packets which are discarded at the mdc

        Also, the perceived arrival rate at the cdc decreases as the size of q1 
        increases, as the mdc is able to process more packets autonomously
        """

        ################# b. Changing the queue length, CDC
        print("2b --------------------")
        for i in range(len(q_lengths)):
            DEBUG = True
            random.seed(seeds[i])
            tmp_res_b.append(
                run(
                    sim_time,
                    fract,
                    serv_t_1=10.0,
                    q1_len=10,
                    serv_t_2=15.0,
                    q2_len=q_lengths[i],
                    results=True,
                )
            )

        ## Plot results:
        # Avg. users in queue 1 (MDC)
        avg_usr_mdc_b = [x[0].ut / sim_time for x in tmp_res_b]

        # Avg. users in queue 2
        avg_usr_cdc_b = [x[1].ut / sim_time for x in tmp_res_b]

        plt.figure(figsize=(10, 5))
        plt.plot(q_lengths, avg_usr_mdc_b, "b", label="Micro Data Center")
        plt.plot(q_lengths, avg_usr_cdc_b, "r", label="Cloud Data Center")
        plt.legend()
        plt.grid()
        plt.title("Average number of users in both queues vs. queue 2 (CDC) size")
        plt.xlabel("Queue 1 length")
        plt.ylabel("Avg. users")
        plt.tight_layout()
        plt.savefig("./images/task2_avg_n_q2_len.png")
        plt.show()

        ################# c. Changing value of f (fraction of packets of type B)
        print("2c --------------------")
        for i in range(len(f_values)):
            DEBUG = False
            random.seed(seeds[i])
            tmp_res_c.append(
                run(
                    sim_time,
                    serv_t_1=10.0,
                    q1_len=10,
                    serv_t_2=15.0,
                    fract=f_values[i],
                    results=True,
                )
            )

        # Plot results (packet drop probability)
        drop_probs_mdc = [x[0].countLosses / x[0].arr for x in tmp_res_c]
        drop_probs_cdc = [x[1].countLosses / x[1].arr for x in tmp_res_c]

        plt.figure(figsize=(8, 4))
        bar_width = 0.4
        x_pos = np.arange(len(f_values))
        plt.bar(x_pos, drop_probs_mdc, width=bar_width, color="b")
        plt.xticks(x_pos, f_values)
        plt.xlabel("Values of f")
        plt.ylabel("Drop probability at micro")
        plt.title("Packet type ratio impact on the drop probability (MDC)")
        plt.tight_layout()
        plt.savefig("./images/task2_loss_prob_mdc.png")

        plt.figure(figsize=(8, 4))
        bar_width = 0.4
        x_pos = np.arange(len(f_values))
        plt.bar(x_pos, drop_probs_cdc, width=bar_width, color="r")
        plt.xticks(x_pos, f_values)
        plt.xlabel("Values of f")
        plt.ylabel("Drop probability at cloud")
        plt.title("Packet type ratio impact on the drop probability (CDC)")
        plt.tight_layout()
        plt.savefig("./images/task2_loss_prob_cdc.png")
        plt.show()

        """
        Comments on point 2:
        - a:
        - b:
        - c: the result seem reasonable, but are still a bit strange; as expected the perceived arrival 
        rate at the cloud increases when more packets of type B are produced, as they need to be 
        processed by CDC
        """

    ################ Task 3. Analysis on packets A average time in the system
    # Threshold T_q to set desired max average time

    if task_3 and T_q is not None:
        print("+------------------ Task 3 ------------------+")

        # a) Find min serv rate to reduce delay A below T_q
        print("+------------------ Task a ------------------+")
        serv_r_list = np.arange(0.1, 0.8, 0.1)
        min_found = False
        delay_list = []
        for serv_r in serv_r_list:
            res_mdc, res_cdc = run(sim_time, fract, serv_t_1=1.0 / serv_r, results=True)

            res_mdc.delay_pkt_A
            total_queuing_delays_A = {}
            for id in res_mdc.delay_pkt_A.keys():
                if id in res_cdc.delay_pkt_A:
                    total_queuing_delays_A[id] = (
                        res_mdc.delay_pkt_A[id] + res_cdc.delay_pkt_A[id]
                    )
                else:
                    total_queuing_delays_A[id] = res_mdc.delay_pkt_A[id]
            max_queuing_delay_A = max(total_queuing_delays_A.values())
            delay_list.append(max_queuing_delay_A)
            if max_queuing_delay_A < T_q and not min_found:
                print(f"\nMinimum service rate is {serv_r}\n")
                min_found = True
        plt.figure()
        plt.title(f"Min serv_r to reduce delay_A below T_q={T_q}")
        plt.grid()
        plt.ylabel("Max delay_A")
        plt.xlabel("serv_rate")
        plt.axhline(T_q, linestyle="--")
        plt.plot(list(serv_r_list), delay_list)
        plt.savefig("lab02/images/serv_r_T_q.png", dpi=300)

        # b) Find min no. of edge nodes to reduce delay A below T_q
        print("+------------------ Task b ------------------+")
        n_serv_list = range(1, 15)
        min_found = False
        delay_list = []
        for n_serv in n_serv_list:
            res_mdc, res_cdc = run(
                sim_time, fract, n_serv_1=n_serv, serv_t_1=8.0, results=True
            )
            total_queuing_delays_A = {}
            for id in res_mdc.delay_pkt_A.keys():
                if id in res_cdc.delay_pkt_A:
                    total_queuing_delays_A[id] = (
                        res_mdc.delay_pkt_A[id] + res_cdc.delay_pkt_A[id]
                    )
                else:
                    total_queuing_delays_A[id] = res_mdc.delay_pkt_A[id]

            max_queuing_delay_A = max(total_queuing_delays_A.values())
            delay_list.append(max_queuing_delay_A)
            # delay_A = (res_cdc.delay_A + res_mdc.delay_A) / (res_cdc.dep + res_mdc.dep)
            # delay_list.append(delay_A)
            if max_queuing_delay_A < T_q and not min_found:
                print(f"\nMinimum no. of edges is {n_serv}")
                min_found = True

        plt.figure()
        plt.title(f"Min n_serv to reduce delay_A below T_q={T_q}")
        plt.grid()
        plt.xlabel("no. of servers")
        plt.ylabel("Max delay_A")
        plt.axhline(T_q, linestyle="--")
        plt.plot(list(n_serv_list), delay_list)
        plt.savefig("lab02/images/n_serv_T_q.png", dpi=300)

        plt.show()

    ########### Task 4. Analysis of the system with multi-server and opertational costs
    if task_4:
        print("+------------------ Task 4 ------------------+")
        # TODO: assign operational cost to each edge node and to the cloud servers

        # a) Vary packet arrival rate over time and analyze system performance
        if task_4a:
            arr_t_list = [8, 3, 2, 12]
            res_mdc, res_cdc = run(
                sim_time,
                fract,
                arr_t=arr_t_list,
                serv_t_1=4.0,
                n_serv_1=4,
                n_serv_2=4,
                results=True,
                plots=True,
            )

        # b)
        if task_4b:
            res_mdc, res_cdc = run(
                sim_time,
                fract,
                arr_t=1.0,
                n_serv_1=4,
                n_serv_2=4,
                serv_t_2=[2, 6, 6, 10],
                server_costs=True,
                results=True,
                plots=False,
            )

        if task_4c and T_q is not None:
            """
            Set a value of f > 0.5 and define a desired threshold on the
            maximum operational cost.
                • Identify the best combination of server types allowing
                to reduce the cost below the desired threshold.
                • Does this combination allow to respect the constraint
                on the maximum queu- ing delay, i.e. Tq, set in Task 3
                for type A packets?
            """
            # NEW fraction
            f = 0.75
            # The operational cost is defined as the rate
            max_oper_cost = 25000  # To be reviewed
            n_serv_2 = 4
            # different server types compinations
            serv_t_list = [[7, 7, 4, 4], [1, 1, 10, 10]]
            print("\n+--------- Task 4c ----------+")
            print(f"\nMaximum cost threshold: {max_oper_cost}")
            print(f"Queuing delay threshold: {T_q}")
            print("+------------------------------------+")
            # TODO: check if constraints of task 3 are respected
            for serv_t_2 in serv_t_list:
                print("\nServer arrival time configuration:", serv_t_2)
                res_mdc, res_cdc = run(
                    sim_time,
                    f,
                    arr_t=1.0,
                    n_serv_1=4,
                    n_serv_2=n_serv_2,
                    serv_t_2=serv_t_2,
                    server_costs=True,
                    results=True,
                )

            if task_4d:
                """
                Install half the number of Cloud servers, keeping the same value
                of f
                    - identify configuration of service types such that the cost
                    is below desired threshold
                    - compare queueing delay and cost under N servers and N/2
                    servers  highlighting how packets of
                    type A and packets of type B are differently affected in terms of delay and
                    packet drop probability
                """
                n_serv_2 = int(n_serv_2 / 2)
                serv_t_list = [[3, 3.97], [10, 10], [1, 1]]
                print("\n\n+--------- Task 4d ----------+")
                for serv_t_2 in serv_t_list:
                    print("\nServer arrival time configuration:", serv_t_2)
                    res_mdc, res_cdc = run(
                        sim_time,
                        f,
                        arr_t=1.0,
                        n_serv_1=4,
                        n_serv_2=n_serv_2,
                        serv_t_2=serv_t_2,
                        server_costs=True,
                        results=True,
                    )
