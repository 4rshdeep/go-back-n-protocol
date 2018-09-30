import socket
import _thread
import sys
import utils
import argparse
from utils import Timer
import time
import random

# Parameters used in this implementation
LOWER_LIMT_PACKET= 64
UPPER_LIMIT_PACKET= 256
WINDOW_SIZE= 7
# WINDOW_SIZE= 7
# WINDOW_SIZE= 9
# WINDOW_SIZE= 2
TIMEOUT=0.5 # give a timeout after 0.5 seconds of no ack
# SENDER_ADDRESS= ('10.0.0.1', 9999)
SENDER_ADDRESS= ('localhost', 9999)
# RECEIVER_ADDRESS=('10.0.0.2', 8080 )
RECEIVER_ADDRESS=('localhost', 8080 )
PERIOD= 0.05

# lock to be used 
lock=_thread.allocate_lock() 
# initialise last ack
last_ack=-1  
# make a timer object to keep track of time
send_timer = Timer(TIMEOUT)

#open file and convert to bytes
def receiving_ack(sock):
    """ Helper function that would run on a thread,
     to keep a check for receiving ack in the senders side """
    global lock
    global last_ack
    global send_timer

    while True:
        # receive packet and extract
        packet = utils.receive_packet(sock)[0]
        ack = utils.extract_packet(packet)[0]
        print("Received Ackowlegement for packet number ",ack )
        # if ack received was greater than what was stored as last 
        # acknoledged ack then sender should increment the last ack variable
        # and stop the timer 
        # if the sender is sending packets this function 
        # would wait till that ends by the means of lock
        if(ack>=last_ack):
            lock.acquire()
            last_ack=ack
            send_timer.stop()
            lock.release()

def sender(filename):
    # main sender function
    global lock
    global last_ack
    global send_timer

    seq_num = 0
    
    # open file for reading 
    file = open(filename, 'rb')
    # open a socket in the sender side
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDRESS)   
    
    # list to store all packets
    all_packets=[]

    while True:
        # packet size which is randomly chosen
        packet_size = (int)(random.randint(LOWER_LIMT_PACKET, UPPER_LIMIT_PACKET+1))
        data_packet = file.read(packet_size)
        
        if not data_packet:
        # if all the packets have been send then break
            break

        # make the data packet and increment the seq_num
        data_packet = utils.make_packet(seq_num, data_packet)
        seq_num += 1

        all_packets.append(data_packet)

    # now that i have created all my data
    num_packets= len(all_packets)
    # sender will be receiving on another thread
    _thread.start_new_thread(receiving_ack,(sock,))


    while last_ack < num_packets-1:
        print("Last ack is ", last_ack) 
        print("Num Packets is ", num_packets) 
        # if the receiving ack business is not done the lock will not be freed
        lock.acquire()
        #send n(window size) packets of size
        for i in range(1,min(WINDOW_SIZE, num_packets-last_ack)):
            #send n packets
            utils.send_packet(all_packets[last_ack+i],sock, RECEIVER_ADDRESS)
            # last_sent=last_ack+i;


        #while waiting for timeout check for acks in between 
        if not send_timer.running():
            # start the timer
            send_timer.start()

        #
        while not send_timer.timeout() and send_timer.running():
            lock.release()
            time.sleep(PERIOD)
            lock.acquire()

        if send_timer.timeout():
            send_timer.stop()
            print("timeout")
        else:
            pass
            #last_ack has been updated in the receive function

        # once all the window has been sent and ack or timeout has occurred begin again 
        lock.release()

    # sending an empty packet to show end of transmission
    utils.send_packet(b'',sock,RECEIVER_ADDRESS)#to confirm completion
    file.close()

    sock.close()

def receive(sock, filename):
    # open file for writing the received packets
    with open(filename, 'wb') as file:
        # starting with the expected frame of sequence number 0
        exp_frame = 0
        while True:
            # get the next packet from the sender
            pkt, addr = utils.receive_packet(sock)
            
            if not pkt:
                # empty packet therefore end of transmission
                break

            # extract the sequence number and data from the packet
            seq_num, data = utils.extract_packet(pkt)

            if seq_num == exp_frame:
                # if the sequence number is equal to the expected frame then send an ack and
                # increment the expected frame number
                pkt = utils.make_packet(exp_frame)
                utils.send_ack(pkt, sock, addr)
                exp_frame += 1
                
                print("Received Sequence number ", seq_num)
                # write the frame into the file
                file.write(data)
            else:
                # send a ack for the last received frame since it might have been 
                # dropped if the expected frame sequence has not come.
                # so that the sender would update it's last ack
                print("Requested Sequence number ", exp_frame-1)
                pkt = utils.make_packet(exp_frame-1)
                utils.send_ack(pkt, sock, addr)


def receiver(filename):
    # open a socket at the receiver's end
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDRESS)
    receive(sock, filename)
    sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--receiver", help="start receiver", action="store_true")
    parser.add_argument("--sender", help="start sender", action="store_true")
    parser.add_argument("--filename", help="File name", type=str, required=True)
    args = parser.parse_args()
    
    if args.receiver:
        print("Started the receiver")
        receiver(args.filename)
    else:
        print("Started the sender")
        sender(args.filename)
