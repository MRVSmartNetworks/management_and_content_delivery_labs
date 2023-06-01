import matplotlib.pyplot as plt
import numpy as np


def printResults(
    n_server,
    server_policy,
    queue_len,
    arr_t,
    serv_t,
    users,
    data,
    time,
    MM_system,
    SIM_TIME,
    img_path,
):
    print(
        "******************************************************************************"
    )

    print("SYSTEM PARAMETERS:\n")
    print(f"Number of servers: {n_server}\nMaximum queue length: {queue_len}")
    print(f"Packet arrival rate: {1./arr_t}\nService rate: {1./serv_t}")

    print(f"\nSimulation time: {SIM_TIME}")

    print(
        "******************************************************************************"
    )
    print(
        "MEASUREMENTS: \n\nNo. of users in the queue (at stop): ",
        users,
        "\nNo. of total arrivals =",
        data.arr,
        "- No. of total departures =",
        data.dep,
    )

    print("Load: ", serv_t / arr_t)
    print(
        "\nMeasured arrival rate: ",
        data.arr / time,
        "\nMeasured departure rate: ",
        data.dep / time,
    )

    print("\nAverage number of users: ", data.ut / time)

    print("\nNumber of losses: ", data.countLosses)

    print("Average delay: ", data.delay / data.dep)
    print("Actual queue size: ", len(MM_system))

    if len(MM_system) > 0:
        print(
            "Arrival time of the last element in the queue:",
            MM_system[len(MM_system) - 1].arrival_time,
        )
    else:
        print("The queue was empty at the end of the simulation")

    print(f"\nAverage waiting delay: ")
    print(
        f"> Considering clients which are not waiting: {np.average(data.waitingDelaysList)}"
    )
    print(
        f"> Without considering clients which did not wait: {np.average(data.waitingDelaysList_no_zeros)}"
    )

    print(f"\nAverage buffer occupancy: {data.avgBuffer/time}")

    print(f"\nLoss probability: {data.countLosses/data.arr}")

    if n_server is not None:
        # The server occupancy only makes sense if the number of servers is
        # finite (and we can define) a policy for the servers utilization
        print("\nBusy Time: ")
        for i in range(n_server):
            print(
                f"> Server {i+1} - cumulative service time: {data.serv_busy[i]['cumulative_time']}"
            )

    print(
        "******************************************************************************"
    )
    # Create name for images (used to determine the parameters)
    if n_server is None:
        n_s = "inf"
    else:
        n_s = str(n_server)

    if queue_len is None:
        n_c = "inf"
    else:
        n_c = str(queue_len)
    fileinfo = f"{n_s}_serv_{n_c}_queue"

    data.queuingDelayHist()
    data.waitingDelayHist()
    data.plotQueuingDelays()
    data.plotServUtilDelay(sim_time=SIM_TIME, policy=server_policy)

    data.plotUsrInTime(img_name=img_path + "usr_time_" + fileinfo + ".png")
    data.queuingDelayHist(
        mean_value=True, img_name=img_path + "hist_delay_" + fileinfo + ".png"
    )
    data.plotQueuingDelays(img_name=img_path + "delay_time_" + fileinfo + ".png")
    data.plotServUtilDelay(
        sim_time=SIM_TIME,
        policy="first_idle",
        img_name=img_path + "serv_util_" + fileinfo + ".png",
    )
    data.plotArrivalsHist(
        mean_value=True, img_name=img_path + "inter_arr_" + fileinfo + ".png"
    )
    data.plotServiceTimeHist(
        mean_value=True, img_name=img_path + "serv_time_" + fileinfo + ".png"
    )
    data.waitingDelayHist(
        zeros=True,
        mean_value=True,
        img_name=img_path + "wait_delay_" + fileinfo + ".png",
    )
    data.waitingDelayHist(
        zeros=False,
        mean_value=False,
        img_name=img_path + "wait_delay_no_zero_" + fileinfo + ".png",
    )


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
    plt.title(
        f"Packets on different arrival rates - queue_len = {param[0]} - n_server = {param[1]} - serv_r= {1./param[2]}"
    )
    plt.plot(
        [1.0 / x for x in arr_t_list],
        [data.arr for data in data_list],
        color="r",
        label="Number of arrival",
    )
    plt.plot(
        [1.0 / x for x in arr_t_list],
        [data.dep for data in data_list],
        color="b",
        label="Number of departure",
    )
    plt.plot(
        [1.0 / x for x in arr_t_list],
        [data.countLosses for data in data_list],
        color="y",
        label="Number of packet loss",
    )
    plt.legend()
    plt.xlabel("arrival rate [1/s]")
    plt.ylabel("no. of packets")
    plt.grid()

    # Average delay plots
    plt.figure()
    plt.title(
        f"Average delay - queue_len = {param[0]} - n_server = {param[1]} - serv_r= {1./param[2]}"
    )
    plt.plot(
        [1.0 / x for x in arr_t_list],
        [np.average(data.waitingDelaysList_no_zeros) for data in data_list],
        label="Average waiting delay (only waiting)",
    )
    plt.plot(
        [1.0 / x for x in arr_t_list],
        [np.average(data.waitingDelaysList) for data in data_list],
        label="Average waiting delay",
    )
    plt.plot(
        [1.0 / x for x in arr_t_list],
        [data.delay / data.dep for data in data_list],
        label="Average delay",
    )
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
    # waitingDelay_no_zeros control for empty list
    # for data in data_list:
    #       if not data.waitingDelaysList_no_zeros:
    #             data.waitingDelaysList_no_zeros = [0]
    # plots for number of packets
    fig = plt.figure(figsize=(10, 5))
    plt.title(
        f"Packets on different arrival rates - arr_r = {round(1./param[0],2)} - n_server = {param[1]} - serv_r= {round(1./param[2], 2)}"
    )
    plt.plot(
        queue_len_list,
        [data.arr for data in data_list],
        color="r",
        label="Number of arrival",
    )
    plt.plot(
        queue_len_list,
        [data.dep for data in data_list],
        color="b",
        label="Number of departure",
    )
    plt.plot(
        queue_len_list,
        [data.countLosses for data in data_list],
        color="y",
        label="Number of packet loss",
    )
    plt.legend()
    plt.xlabel("queue length")
    plt.ylabel("no. of packets")
    plt.grid()
    plt.savefig("lab01/report/images/queueVar_MM2.png")

    # Average delay plots
    fig = plt.figure(figsize=(10, 5))
    plt.title(
        f"Average delay - arr_r = {round(1./param[0],2)} - n_server = {param[1]} - serv_r= {round(1./param[2], 2)}"
    )
    plt.plot(
        queue_len_list,
        [
            0
            if not data.waitingDelaysList_no_zeros
            else np.average(data.waitingDelaysList_no_zeros)
            for data in data_list
        ],
        label="Average waiting delay (only waiting)",
    )
    plt.plot(
        queue_len_list,
        [np.average(data.waitingDelaysList) for data in data_list],
        label="Average waiting delay",
    )
    plt.plot(
        queue_len_list,
        [data.delay / data.dep for data in data_list],
        label="Average delay",
    )
    plt.legend()
    plt.ylabel("waiting delay [s]")
    plt.xlabel("queue length")
    plt.grid()
    plt.savefig("lab01/report/images/queueVar_del_MM2.png")

    plt.show()


def plotConfInter(
    metric_name, n_iter, conf_level, intervals, metric_cf_mean, arr_t_list
):
    plt.figure()
    plt.title(
        f"Confidence intervals for {metric_name} - df={n_iter-1} - conf_level={conf_level}"
    )
    plt.plot([1.0 / x for x in arr_t_list], metric_cf_mean)
    plt.fill_between(
        [1.0 / x for x in arr_t_list],
        list(zip(*intervals))[0],
        list(zip(*intervals))[1],
        color="r",
        alpha=0.2,
    )
    plt.xlabel("Arrival rate")
    plt.ylabel(f"{metric_name}")
    plt.grid()
    # plt.savefig(f'lab01/report/images/{metric_name}_conf_int.png')
    plt.show()
