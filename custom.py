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

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    r4 = net.addHost('r4', cls=Node, ip='0.0.0.0')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    r5 = net.addHost('r5', cls=Node, ip='0.0.0.0')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
    d1 = net.addDocker('d1', ip = '10.0.0.251',dimage="ubuntu:trusty")
    d2 = net.addDocker('d2', ip = '10.0.0.252',dimage="ubuntu:trusty")
    d3 = net.addDocker('d3', ip = '10.0.0.253',dimage="ubuntu:trusty")

    info( '*** Add links\n')
    net.addLink(d3, s3)
    net.addLink(d1, s1)
    net.addLink(d2, s2)
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s3, h5)
    net.addLink(s3, h6)
    net.addLink(s2, h3)
    net.addLink(s2, h4)
    net.addLink(d1, r4)
    net.addLink(d1, r5)
    net.addLink(r4, r5)
    net.addLink(d3, r4)
    net.addLink(d3, r5)
    net.addLink(d2, r5)
    net.addLink(d2, r4)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([])
    net.get('s2').start([])
    net.get('s3').start([])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
