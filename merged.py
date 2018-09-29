import socket
import _thread
import sys
import numpy as np
import utils
import argparse
from utils import Timer
import time

LOWER_LIMT_PACKET= 64
UPPER_LIMIT_PACKET= 256
WINDOW_SIZE= 7
TIMEOUT=0.5
SENDER_ADDRESS= ('0.0.0.0', 9999)
RECEIVER_ADDRESS=('0.0.0.0', 8080 )
PERIOD= 0.05

#open file and convert to bytes
lock=_thread.allocate_lock()
last_ack=-1
send_timer = Timer(TIMEOUT)

def receiving_ack(sock):
    global lock
    global last_ack
    global send_timer

    while True:
        packet = utils.receive_packet(sock)[0]
        ack = utils.extract_packet(packet)[0]
        print("Received Ackowlegement for packet number ",ack )
        if(ack>=last_ack):
            lock.acquire()
            last_ack=ack
            send_timer.stop()
            lock.release()

def sender(filename):
    global lock
    global last_ack
    global send_timer

    seq_num = 0
    
    file = open(filename, 'rb')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDRESS)   
    all_packets=[]

    while True:
        packet_size = (int)(np.random.uniform(LOWER_LIMT_PACKET, UPPER_LIMIT_PACKET+1))
        data_packet = file.read(packet_size)
        
        if not data_packet:
            print(data_packet)
            break

        data_packet = utils.make_packet(seq_num, data_packet)
        seq_num += 1

        #means we must have created all our data.
        all_packets.append(data_packet)

    # now that i have created all my data
    num_packets= len(all_packets)
    _thread.start_new_thread(receiving_ack,(sock,))


    # last_sent=-1
    while last_ack < num_packets-1:
        print("Last ack is ", last_ack) 
        print("Num Packets is ", num_packets) 
        lock.acquire()
        #send n(window size) packets of size
        for i in range(1,min(WINDOW_SIZE, num_packets-last_ack)):
            #send n packets
            utils.send_packet(all_packets[last_ack+i],sock, RECEIVER_ADDRESS)
            # last_sent=last_ack+i;


        #while waiting for timeout check for acks in between 
        if not send_timer.running():
            send_timer.start()

        #i think we can take the release and acquire out of the loop
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

        lock.release()

    utils.send_packet(b'',sock,RECEIVER_ADDRESS)#to confirm completion
    file.close()

    sock.close()

def receive(sock, filename):
    with open(filename, 'wb') as file:
        exp_frame = 0
        while True:
            # get the next packet from the sender
            pkt, addr = utils.receive_packet(sock)
            
            if not pkt:
                # sentinel is empty packet therefore end of transmission
                break
            # print(pkt)
            seq_num, data = utils.extract_packet(pkt)

            if seq_num == exp_frame:
                pkt = utils.make_packet(exp_frame)
                utils.send_packet(pkt, sock, addr)
                exp_frame += 1
                print("Received Sequence number ", seq_num)
                file.write(data)
            else:
                print("Requested Sequence number ", exp_frame-1)
                pkt = utils.make_packet(exp_frame-1)
                utils.send_packet(pkt, sock, addr)


def receiver(filename):
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
