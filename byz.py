import zmq
import sys
import random
import argparse
import time
from threading import Thread
from queue import Queue
from anytree import AnyNode, RenderTree, Node, PreOrderIter

class Sender(Thread):
    # get message from queue
    # process the message - e.g. add to tree
    # send to other generals after appending your own id
    def __init__(self, queue, req_socket, ports,fault, my_ID):
        Thread.__init__(self)
        self.queue = queue
        self.req_socket = req_socket
        self.ports = ports
        self.fault=fault
        self.my_ID=my_ID
        self.Node_ID=dict()

    def send(self, msg,recv_fromID):
        for p in self.ports:
            
            self.req_socket.connect("tcp://localhost:{}".format(p))
            self.req_socket.send(msg)
            print("Sending message {} to {}".format(msg,p))
            rep = self.req_socket.recv()
            self.req_socket.disconnect("tcp://localhost:{}".format(p))

    def flip(self,recv_bit):
        if(recv_bit==1):
            #print("Flipping received bit 1 to 0")
            recv_bit=0
        else:
            #print("Flipping received bit 0 to 1")
            recv_bit=1
        return recv_bit

    def poll(self,ID):
        print("Inside poll function: {}".format(ID))
        me = self.Node_ID[ID]
        if (me.is_leaf):
            me.output = me.value
        else:
            ones = 0
            zeros = 0
            for n in me.children:
                self.poll(n.name)
                if(n.output==1):
                    ones=ones+1
                else:
                    zeros=zeros+1
            if (ones > zeros):
                me.output = 1
            else:
                me.output = 0
            return me.output

    def run(self):
        
        while True:
            msg = self.queue.get()
            print("Getting messages from queue",msg)
            recv_bit,recv_ID=msg.split(',')
            recv_fromID=recv_ID[-1]
            #print("Bit received before fault",recv_bit)
        
            print("Received from ",recv_fromID)
            parent_node=recv_ID[:len(recv_ID)-1]

            if len(recv_ID)==1:
                self.Node_ID[recv_ID]=Node(recv_ID,value=int(recv_bit),output='?')
            else:
                self.Node_ID[recv_ID]=Node(recv_ID,parent=self.Node_ID[parent_node],value=int(recv_bit),output='?')
                            
            if(self.fault):
                #print("Satisfies fault condition")
                recv_bit=self.flip(int(recv_bit))

            if(str(self.my_ID)==recv_fromID):
                continue

            if len(recv_ID)==3: #This is to configure number of rounds
                decision=self.poll('1')
                print(RenderTree(self.Node_ID['1']))
                print("Final decision: ",decision)
                continue

            new_message=str("{},{}{}".format(recv_bit,recv_ID,self.my_ID))
            self.send(new_message.encode('utf-8'),recv_fromID)
        

class Receiver(Thread):
    def __init__(self, queue, rep_socket, my_port,fault,my_ID):
        Thread.__init__(self)
        self.queue = queue
        self.rep_socket = rep_socket
        self.my_ID=my_ID
        self.fault=fault

    def run(self):
        
        while True:
            time.sleep(1)
            msg = self.rep_socket.recv()
            msg=msg.decode()
            print("Received message: ",msg)
            self.rep_socket.send(b"Recvd")
            self.queue.put(msg)
            print("Putting on queue, msg: {}".format(msg))
            

def main():
    parser = argparse.ArgumentParser(description='Byzantine Fault Tolerance')
    parser.add_argument('ports', metavar='ports', type=int, nargs='+',
                                        help='other ports to connect')
    parser.add_argument('-me', '--my_port', type=int, nargs='?',
                                        help='my port')
    parser.add_argument('--primary', action='store_true', help='is this node primary')
    parser.add_argument('--fault',action='store_true', help='is this node faulty')
    
    args = parser.parse_args()
    print(args.ports)
    print(args.my_port)
    print(args.primary)

    queue=Queue() # a queue for sharing messages between sender & receier threads
    
    context=zmq.Context()
    rep_socket = context.socket(zmq.REP)
    req_socket = context.socket(zmq.REQ)

    if (args.primary):
        my_ID=1
        bit=random.randint(0,1)
        # sending a bunch of kick starter messages
        for p in args.ports:
            req_socket.connect("tcp://localhost:{}".format(p))
            message=str("{},{}".format(bit,my_ID))
            req_socket.send(message.encode('utf-8'))
            rep = req_socket.recv()
            print(rep)
            req_socket.disconnect("tcp://localhost:{}".format(p))

    else:
        i=2
        for prt in args.ports:
            #print("Iterating over ports",prt)
            if(prt==args.my_port):
                print("Port: ",prt)
                my_ID=i
                print("My ID: ",my_ID)
            i+=1
    
        # not primary - bind rep socket, start a sender and receiver thread
        rep_socket.bind("tcp://*:{}".format(args.my_port))
        print("Server started listening on {}".format(args.my_port))
        Receiver(queue, rep_socket, args.my_port,args.fault,my_ID).start()
        Sender(queue, req_socket, args.ports,args.fault,my_ID).start()
        
    while True:
        time.sleep(20)
        print("...")


if __name__ == '__main__':
    main()
