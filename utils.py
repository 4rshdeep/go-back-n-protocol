import random
import socket
import time

# functions to send and receive packets
def send_packet(packet, sock, addr):
    sock.sendto(packet, addr)
    return

def receive_packet(sock):
    packet, addr = sock.recvfrom(1024)
    return packet, addr

def make_packet(seq_num, data=b''):
    seq_bytes = seq_num.to_bytes(4, byteorder='little', signed=True)
    #add checksum here
    return seq_bytes + data

def extract_packet(packet):
    # try changing byte order
    seq_num = int.from_bytes(packets[:4], byteorder='little', signed=True)

def make_empty_packet():
    return b''

class Timer(object):
    
    def __init__(self, duration):
        self._start_time = -1
        self._duration = duration

    def start(self):
        if self._start_time == -1:
            self._start_time = time.time()

    def stop(self):
        if self._start_time != -1:
            self._start_time = -1

    def running(self):
        return self._start_time != -1

    def timeout(self):
        if not self.running():
            return False
        else:
            return time.time() - self._start_time >= self._duration