import socket
import _thread
import sys
import numpy as np
import utils
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

def main():
    global lock
    global last_ack
    global send_timer

    seq_num = 0
    
    file = open(sys.argv[1], 'rb')
    print(sys.argv[1])
    # exit()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDRESS)   
    all_packets=[]

    while True:
        print("making packets")
        #create all packets
        # packet_size = (int)(np.random.uniform(LOWER_LIMT_PACKET, UPPER_LIMIT_PACKET+1))
        # print(packet_size)
        data_packet = file.read(UPPER_LIMIT_PACKET)
        
        if not data_packet:
            # print("***")
            print(data_packet)
            # exit()
            break

        # print(data_packet)
        data_packet = utils.make_packet(seq_num, data_packet)
        seq_num += 1

        #means we must have created all our data.
        all_packets.append(data_packet)

    # exit()
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

if __name__ == '__main__':
    main()
