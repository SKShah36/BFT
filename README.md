## Byzantine Fault Tolerance

## Description
In order to implement the byzantine fault tolerance algorithm we are using 7 different nodes connected to each other.
In this program, ID 1 is assigned the primary general and is assumed not faulty who sends out the messages to all the other six IDs starting from 2 upto 7.

This program runs upto three rounds: 
Round 0-where the general sends out messages to all other nodes

Round 1-where each IDs(process) having received a message from the general sends out another message in the format (general's message,general'sid-myid). For example if ID2 receives 0 from ID1 as message in the form 0,1 then it sends out 0,12 to other IDs including itself but excluding the general, where 2 is its own ID that it has appended to the message.

Round 2-In the same manner as Round 1, the IDs append their own ID to the received message and forward it to each other.

Number of rounds are hardcoded in the program but can be configured (See comments in the program)

## Assumptions:
1. There are at maximum only two faulty nodes.
2. All nodes/IDs are up and running before messages are being sent out by the primary.
3. In case where consensus cannot be formed we go with 0 as the decision for a node.
 

## Running the program:

If we are running 7 processes then we start by setting up the lieutenant nodes by using the following commands in multiple tabs:

```python3 byz.py 8002 8003 8004 8005 8006 8007 -me (my_port) ```  #where my_port is port number\
```For e.g. python3 byz.py 8002 8003 8004 8005 8006 8007 -me 8002 ```     #This sets up the server listening on 8002

In order to designate a node as faulty we will pass the --fault argument to the program. This is done using:

```python3 byz.py 8002 8003 8004 8005 8006 8007 -me (my_port) --fault ```\
``` For e.g. python3 byz.py 8002 8003 8004 8005 8006 8007 -me 8002 --fault  ``` #Ensure only two nodes are assigned faulty at max.\
Once done setting up the servers, then we are good to go and launch the primary general's process which is done as follows:

```python3 byz.py 8002 8003 8004 8005 8006 8007 --primary```


At the end of each program you will see the final decision in terms of 0 or 1.

