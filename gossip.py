#!usr/local/bin/python

#Patrick Coe 14008988

#(148008988%5) + 1 == 4
#Gossiping
#
#First time ever using the python programming language, or any higher level programming language for that matter
#also learned a bit more bash and batch in order to automate testing
# - was a very strong learning experience.
#
#written in python version 3.2.2
#resources used: - http://www.tutorialspoint.com/python/python_networking.htm - in order to understand how to use sockets, network code may look similar.
#                - Python Library

#in case of any confusion.
#regardless of how many nodes are contacted per gossip, it is still one gossip. fowarding gossip's are not counted towards the gossip count.
#
#problems with send/receive. cannot receive while sending. cannot send while receiving. This leads to some lost messages and a fairly long run time.
#might need to look into more advanced multi-threaded programming.


import sys
#import shlex
import re
import socket
import random
import struct
import time

try:
    myID = sys.argv[2]              #playing around with exeptions. This will get the ID, and if not available let the user know
except IndexError:
    print("\n \nNo ID has been given. ID must be given as an integer.")
    print("\nPlease use the following format: \n \n    gossip.pf [filename] [ID]")

gossips_sent = 0    #count of gossip messages sent
gossips_received = 0#count of gossip messages received

def send_gossip():  #gossip send function

        gossipID = str(random.randint(0,500))    #gossip message consists of a unique ID -should use time instead to make variable unique
        gossip_message = gossipID + " " + myID
        

        for count in range (0, 3):     #each gossip contacts 3 nodes       

            for count in range (0,5):      #if node is busy, will try another node until send is succesful, or send limit is reached
                try:
                   rand_num = random.randint(0,len(hosts)-1)   #number used to pick a random node
                   print("sending gossip", (str(hosts[rand_num])), " on port ", str(ports[rand_num])) #prints info to user
                   s = socket.socket()  #open socket
                   s.connect((str(hosts[rand_num]), int(ports[rand_num]))) #initiate connection with node -if error there will be an exception
                   s.send(bytes(str(gossip_message), 'UTF-8')) #send data in byte form
                   s.close #close socket
                   output.write(" s " + gossipID + " [ "  + myID + " ] ") #write data to output file using assigned format s i [ v ]
                   break #if reached this point send is succesful, break out of loop
                except:         #exception, error message give, maximum 5 retries.
                    pass
                    if count == 5:
                        print("gossip failed.")
                    else:
                        print("connection error, message not sent. Will try different node.")
                        #count +=1   - not needed??
        

def receive_gossip():     #receive function
        s = socket.socket()   #open socket
        s.settimeout(120)     #set timeout so that node is not indefinately listening
        print("waiting for gossip")
        s.bind((str(myhost),int(myport))) #bind this nodes host and port to socket

        s.listen(5)   #listen
        c, addr = s.accept()     # Establish connection with client.
        print ('Got connection from', addr)
        temp_message = c.recv(1024).decode('UTF-8') #decode byte message
        print("Message received: ", temp_message) #print message
        c.close()                # Close connection

        gossip_message_pass = re.findall("[0-9.]+", str(temp_message)) #seperate data in received message into usable format

        #print(gossip_message_pass) #print message

        if str(myID) in gossip_message_pass:   #If this nodes ID is already in the message, pass it to IDcheck, gossip should not be forwarded
            IDcheck = gossip_message_pass.index(myID)
        else:  #if not, assign 0, gossip will be forwarded
            IDcheck = 0
       # if IDcheck == 0:  #if in position 0, then -this is a mistake, because unique ID could match node ID, and node ID may be further along in the message
       #     IDcheck = 0   #these two lines of code essentially do nothing for this reason. Still, the case where the unique ID and node ID match needs to be taken care of.

        count = 0 #set  count to 0
        output.write(" r " + gossip_message_pass[0] + " [")  #output data to file
        while count < (len(gossip_message_pass)-1):   # go through all vectors and write to file
             output.write(" " + gossip_message_pass[count+1])
             count += 1
        output.write(" ]")
        
        count = 0 #set count back to 0 --- is this necessary?
        

        if IDcheck != 0:    #if ID check is not 0, this means the ID is in the vector and should not be forwarded as it has already been forwarded by this node.
                print("do not pass")
                
        else: #else, pass the gossip along
            for count in range (0, 3):     #if all criteria is met, forward received gossip to nodes 3 times
                print("passing gossip")
                
                gossip_message = " ".join(gossip_message_pass) + " " + myID #join message back into a single string in preperation to be sent over the network

                for count in range (0,5):   #just as in the send function, make 5 attempts to send a message incase node is busy
                    try:
                       rand_num = random.randint(0,len(hosts)-1)   #don't pick previous ID
                       while rand_num == gossip_message_pass[len(gossip_message_pass) - 1]: #the last ID is the previous node
                           rand_num = random.randint(0,len(hosts)-1)    #from my understanding, only the last node needs to be checked, ex. randnum = 2, previous nodes = 2, 3, 5.
                                                                        #randnum is valid since this node did not receive message from 2.

                       print("forwarding gossip", (str(hosts[rand_num])), " on port ", str(ports[rand_num])) #prints info to user
                           
                       s = socket.socket()
                       s.connect((str(hosts[rand_num]), int(ports[rand_num])))  #connect to a random node waiting for gossip, if error, check exception
                       s.send(bytes(str(gossip_message), 'UTF-8')) #send byte data
                       s.close #close socket

                       output.write(" s " + gossip_message_pass[0] + " [")    #write send info to output file
                       count = 0 #make sure count starts at 0
                       while count < (len(gossip_message_pass)-1):
                           output.write(" " + gossip_message_pass[count+1]) #can't remember why count + 1.... check this. - and now I remember. item 0 is the gossip ID.
                           count += 1
                       output.write(" " + myID + " ]") #append my ID

                       break #break loop if send succeful
                       
                    except:
                        pass
                        if count == 5:    
                            print("node not responding.")
                        else:
                            print("connection error, message not sent. Will try different node.")
            
            
#-------------------
#opens file based on command line argument, reads lines from text as a string, seperates config data
cfg_lines = re.findall("[0-9.]+", str(open(sys.argv[1], 'r').readlines())) 

IDs = []    #initializing lists
hosts = []
ports = []

for count in range(0,(len(cfg_lines))): #seperate  hosts, IDs, and ports into seperate lists for easier management
    if count%3 == 0:
        IDs.append(cfg_lines[count])
    if count%3 == 1:
        hosts.append(cfg_lines[count])
    if count%3 == 2:
        ports.append(cfg_lines[count])

#----------------

#myIDpos = IDs.index(myID) find position of my ID, to figure out associated port number

output = open('output' + myID + '.txt','w') #open outputfile for writing

myhost = hosts[IDs.index(myID)]   #set hosts and ports to easier to use variables
myport = ports[IDs.index(myID)]


if int(myID) == 1: #begin gossip if first ID
    send_gossip()    
    gossips_sent += 1

receive_gossip()
gossips_received += 1

send_gossip()    #send one gossip after first gossip is received
gossips_sent += 1 #regardless of how many nodes are contacted, this is considered one gossip. fowarding gossip's are not considered gossip for this count.

for count in range(0,4): #thereafter send one gossip every 5 gossips received
    receive_gossip()
    gossips_received += 1

send_gossip()  
gossips_sent += 1
    
while int(gossips_sent) < 10: #when 10 gossips are sent program is done running.
    for count in range(0,4): #still with the one gossip every 5 gossips received
        receive_gossip()
    send_gossip()
    gossips_sent += 1
    print("gossips sent:", gossips_sent) #for debug perposes.
    
print("good-bye")
