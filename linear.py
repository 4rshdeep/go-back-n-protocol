#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

class SingleSwitchTopo( Topo ):
    """ Single switch connected to n hosts. This would be then used to run our experiments on mininet """
    
    # function to create a topology with two hosts
    def build( self, n=2 ):
        switch = self.addSwitch( 's1' )
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost( 'h%s' % (h + 1) )
            # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
            self.addLink( host, switch, bw=1 )
        
def perfTest():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo( n=2 )
    net = Mininet( topo=topo, host=CPULimitedHost, link=TCLink )
    net.start()
    # creating a cli for running out experiments
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    perfTest()