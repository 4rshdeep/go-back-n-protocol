#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.util import dumpNodeConnections

def LinearTopo(n=10):

    net = Mininet( topo=None, host=CPULimitedHost, link=TCLink, build=False )

    net.addController('c0', controller=RemoteController,ip="127.0.0.1",port=6633)

    
    hosts = []
    switches = []
    for i in range(n):
        hosts.append(net.addHost( 'h' + str(i) ))
        switches.append(net.addSwitch( 's' + str(i), cls=OVSSwitch ))
        # net.addLink(hosts[i], switches[i], bw=10)
        net.addLink(hosts[i], switches[i], delay=1000)
        # print("Connection added between " + str(hosts[i]) + " and "+str(switches[i]))

    for i in range (len(switches)-1):
        # net.addLink(switches[i], switches[i+1])
        net.addLink(switches[i], switches[i+1], delay=1000)
        # print("Connection added between " + str(switches[i]) + " and "+str(switches[i+1]))

    # info( '*** Starting network\n')
    net.start()

    for i in range(1, len(switches)):
        switches[i].cmd('ifconfig switch' + str(i) + ' 10.0.1.' + str(i))
        switches[i].cmd('ovs-vsctl set bridge switch'+str(i)+' stp-enable=true')
    
    # info( '*** Running CLI\n' )
    # CLI( net )
    net.pingAll()
    perfTest(net, hosts)

    # info( '*** Stopping network' )
    net.stop()

def perfTest(net, host):
    # print "Dumping host connections"
    dumpNodeConnections( net.hosts )
    # print "Testing network connectivity"
    net.pingAll()
    # print "Testing bandwidth between h1 and h4"
    # h1, h4 = net.get( 'h1', 'h4' )
    # h3, h9 = net.get( 'h3', 'h9' )

    net.ping(hosts=[host[1], host[4]])
    net.ping(hosts=[host[3], host[9]])

    net.iperf( )
    net.iperf( hosts=[host[1], host[8]] )

    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    LinearTopo()
