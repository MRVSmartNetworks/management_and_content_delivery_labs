# management_and_content_delivery_labs

Laboratories for the course Management and Content Delivery for Smart Networks @ Politecnico di Torino; A.Y. 2022/2023

## Lab 1

The first laboratory consists in building a model and analyzing the behavior of a queuing system under various configurations.
The baseline scenario is that of a simple M/M/n queuing system (using Kendall's notation).

## Lab 2

The second laboratory includes a model for an Industrial IoT system composed of two queues, representing two processing stages in the system.

The system is composed of a 'Micro Data Center', which processes data at the edge, and a 'Cloud Data Center', which instead processes data at the cloud level.
These queuing network is made up of a tandem connection of the two, in order, and it processes packets which are produced by sensors.
These packets can be of two types:

* Type A: they are time-sensitive packets, which are just processed at the edge.
* Type B: these packets need to be pre-processed at the edge level, and then sent to the Cloud Data Center.

Whenever the first queue (Micro Data Center) is full, packets are directly forwarded to the second one, regardless of their type.

The analysis concerns a series of simulations which aim at evaluating the system performance in different scenarios, including time-dependent packet arrival rates (simulating traffic dependence on the time of the day), or analyses on the cost of operating the system, having assigned the servers a price depending on their performance.
Different policies for server assignment in multi-server queues have also been implemented and compared.

