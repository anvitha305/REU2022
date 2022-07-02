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
    r4 = net.addHost('r4', cls=Node, ip='0.0.0.0')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    r5 = net.addHost('r5', cls=Node, ip='0.0.0.0')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    d1 = net.addDocker('d1', ip = '10.0.251.10',dimage="ubuntu:trusty")
    d2 = net.addDocker('d2', ip = '10.0.252.10',dimage="ubuntu:trusty")
    d3 = net.addDocker('d3', ip = '10.0.253.10',dimage="ubuntu:trusty")

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.10', defaultRoute='via 10.0.0.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.2.10', defaultRoute='via 10.0.0.2')
    h3 = net.addHost('h3', cls=Host, ip='10.0.3.10', defaultRoute='via 10.0.0.3')
    h4 = net.addHost('h4', cls=Host, ip='10.0.4.10', defaultRoute='via 10.0.0.4')
    h5 = net.addHost('h5', cls=Host, ip='10.0.5.10', defaultRoute='via 10.0.0.5')
    h6 = net.addHost('h6', cls=Host, ip='10.0.6.10', defaultRoute='via 10.0.0.6')

    info( '*** Add links\n')
    net.addLink(r4, r5)
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(d1, s1)
    net.addLink(d1, s4)
    net.addLink(s4, r5)
    net.addLink(s4, r4)
    net.addLink(s5, r4)
    net.addLink(s5, r5)
    net.addLink(s6, r5)
    net.addLink(s6, r4)
    net.addLink(d2, s6)
    net.addLink(d2, s2)
    net.addLink(s2, h3)
    net.addLink(s2, h4)
    net.addLink(s3, h5)
    net.addLink(s3, h6)
    net.addLink(d3, s3)
    net.addLink(d3, s5)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('s4').start([c0])
    net.get('s6').start([c0])
    net.get('s5').start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
