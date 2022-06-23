#!/usr/bin/python
"""

This is the topology that Michael and I designed
on 6/16/22 at ~ 1:30PM
[three containers, three congestions]

author: Anvitha
date: 6/16/22 at ~ 9:45PM
"""
from mininet.net import Containernet
from mininet.topo import Topo
from mininet.node import Node, Controller
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from router import LinuxRouter

class NetworkTopo(Topo):
    def build(self, **_opts):
        setLogLevel('info')
        net = Containernet(controller=Controller)
        # not adding a controller !!! [controller ??? i hardly know  her]
        #info('*** Adding controller\n')
        #net.addController('c0')

        info('*** Adding routers\n')
        routers = []
        for i in range(2):
            routers.append(self.addNode(name = 'r%s'%(i+1), cls=LinuxRouter, ip = '192.168.1.%s/24'%(i+1)))

        info('*** Adding switches\n')
        switches = []
        for i in range(3):
            switches.append(self.addSwitch('s%s'%(i+1)))
        #dockers = []
        #for i in range(1,4):
        #    dockers.append(net.addDocker('d%s'%(i), ip = '10.0.0.25%s'%(i),dimage="ubuntu:trusty"))

        info('*** Adding hosts\n')
        hosts = []
        for h in range(3):
            for i in range(2):
                    hosts.append(self.addHost('h%s.%s' % (h+1, i+1)))
                    self.addLink(hosts[h*2 + i], switches[i])
                    #self.addLink(dockers[h], hosts[h*2 + i])

        #info('*** Creating links\n')
        #for i in range(len(switches)):
        #    for r in routers:
        #        net.addLink(switches[i], r, intfName2='r0-eth%s'%(i+1),)


def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo,waitConnected=True )  # controller is used by s1-s3
    net.start()
    info( '*** Routing Table on Router:\n' )
    CLI( net )
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
