#!/usr/bin/python
"""

This is the topology that Michael and I designed
on 6/16/22 at ~ 1:30PM
[three containers, three congestions]

author: Anvitha
date: 6/16/22 at ~ 9:45PM
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import router
setLogLevel('info')

net = Containernet(controller=Controller)
# not adding a controller !!! [controller ??? i hardly know  her]
#info('*** Adding controller\n')
#net.addController('c0')


info('*** Adding switches\n')
switches = []
for i in range(3):
    switches.append(net.addSwitch('s%s'%(i+1)))
dockers = []
for i in range(1,4):
    dockers.append(net.addDocker('d%s'%(i), ip = '10.0.0.25%s'%(i),dimage="ubuntu:trusty"))

info('*** Adding hosts\n')
hosts = []
for h in range(3):
    for i in range(2):
            hosts.append(net.addHost('h%s.%s' % (h+1, i+1)))
            net.addLink(hosts[h*2 + i], switches[i])
print(hosts)
info('*** Adding docker containers\n')


# d1 = net.addDocker('d1', ip='10.0.0.251', dimage="ubuntu:trusty", devices=[s1])
# d2 = net.addDocker('d2', ip='10.0.0.252', dimage="ubuntu:trusty")
# d3 = net.addDocker('d3', ip='10.0.0.253', dimage="ubuntu:trusty")
#

info('*** Adding routers\n')
routers = []
for i in range(2):
    routers.append(net.addNode('r%s'%(i+1), cls=LinuxRouter, ip = '192.168.1.%s/24'%(i+1)))


info('*** Creating links\n')
for s in switches:
    for r in routers:
        net.addLink(s, r)
net.addLink(r[0], r[1])


info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([d1, d2])
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
