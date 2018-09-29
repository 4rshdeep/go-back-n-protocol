import packet
import socket
import sys
import utils

RECEIVER_ADDR = ('localhost', 8080)

def receive(sock, filename):

    with open(filename, 'wb') as file:
    
        exp_frame = 0
        while True:
            # get the next packet from the sender
            pkt, addr = utils.receive_packet(sock)
            
            if not pkt:
                # sentinel is empty packet therefore end of transmission
                break

            seq_num, data = utils.extract_packet(pkt)

            if seq_num == exp_frame:
                pkt = utils.make_packet(exp_frame)
                utils.send_packet(pkt, sock, addr)
                exp_frame += 1
                file.write(data)
            else:
                pkt = utils.make_packet(exp_frame-1)
                utils.send_packet(pkt, sock, addr)


def main():
    if len(sys.argv)!=2:
        exit()
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(RECEIVER_ADDR)
        filename = sys.argv[1]
        receive(sock, filename)
        sock.close()

if __name__ == '__main__':
    main()