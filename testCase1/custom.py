#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
from mininet.net import Containernet

def myNetwork():

    net = Containernet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    r4 = net.addHost('r4', cls=Node, ip='0.0.1.0')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    r5 = net.addHost('r5', cls=Node, ip='0.0.2.0')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    d2 = net.addDocker('d2', ip = '10.0.2.10/24', dimage="ubuntu:trusty")
    d3 = net.addDocker('d3', ip = '10.0.3.10/24', dimage="ubuntu:trusty")

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2')
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3')
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4')
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5')
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6')

    info( '*** Add links\n')
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s2, h3)
    net.addLink(s2, h4)
    net.addLink(s3, h5)
    net.addLink(s3, h6)
    net.addLink(s1, r4)
    net.addLink(s1, r5)
    net.addLink(r4, r5, params2={ 'ip' : '172.16.0.3/12'},intfName2='r5-eth6')
    net.addLink(s1, r4,params2={ 'ip' : '172.16.0.1/12'},intfName2='r4-eth5')
    net.addLink(s1, r5,params2={ 'ip' : '172.16.0.2/12'},intfName2='r5-eth5')
    net.addLink(s2, r4)
    net.addLink(s2, r5)
    net.addLink(s3, r4)
    net.addLink(s3, r5)
    net.addLink(d2, s2)
    net.addLink(d3, s3)


    info( '*** Starting network\n')
    net.build()

    info( '*** Starting switches\n')
    c0.start()
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])

    info( '*** Post configure switches and hosts\n')
    r4.cmd("ifconfig r4-eth2 0")
    r4.cmd("ifconfig r4-eth3 0")
    r4.cmd("ifconfig r4-eth4 0")
    #r4.cmd("ifconfig r4-eth2 hw ether 00:00:00:00:01:02")
    #r4.cmd("ifconfig r4-eth3 hw ether 00:00:00:00:01:03")
    r4.cmd("ip addr add 10.0.2.1/24 brd + dev r4-eth2")
    r4.cmd("ip addr add 10.0.3.1/24 brd + dev r4-eth3")
    r4.cmd("ip addr add 0.0.2.0/24 brd + dev r4-eth4")
    d2.cmd("ip route add 10.0.2.1")
    d3.cmd("ip route add 10.0.3.1")

    r5.cmd("ifconfig r5-eth2 0")
    r5.cmd("ifconfig r5-eth3 0")
    r4.cmd("ifconfig r5-eth4 0")
    r5.cmd("ip addr add 10.0.2.2/24 brd + dev r5-eth2")
    r5.cmd("ip addr add 10.0.3.2/24 brd + dev r5-eth3")
    r5.cmd("ip addr add 0.0.1.0/24 brd + dev r5-eth4")
    d2.cmd("ip route add 10.0.2.2")
    d3.cmd("ip route add 10.0.3.2")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
