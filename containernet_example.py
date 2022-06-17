#!/usr/bin/python
"""
<<<<<<< HEAD

This is the topology that Michael and I designed
on 6/16/22 at ~ 1:30PM
[three containers, three congestions]

author: Anvitha
date: 6/16/22 at ~ 9:45PM
=======
This is the most simple example to showcase Containernet.
>>>>>>> 696531eda02cb1324510889ba494d2b8f3c70f77
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
<<<<<<< HEAD
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
info('*** Adding hosts\n')
hosts = []
for h in range(3):
    for i in range(2):
            hosts.append(net.addHost('h%s.%s' % (h+1, i+1)))
            net.addLink(hosts[h*3 + i], switches[i])

info('*** Adding docker containers\n')

dockers = []
for i in range(1,4):
    dockers.append(net.addDocker('d%s'%(i), ip = '10.0.0.25%s'%(i),
        dimage="ubuntu:trusty", devices=hosts[3*(i-1):3*(i-1)+3 ]))
# d1 = net.addDocker('d1', ip='10.0.0.251', dimage="ubuntu:trusty", devices=[s1])
# d2 = net.addDocker('d2', ip='10.0.0.252', dimage="ubuntu:trusty")
# d3 = net.addDocker('d3', ip='10.0.0.253', dimage="ubuntu:trusty")
#

info('*** Adding routers\n')
r1 = net.addNode('r1', cls=LinuxRouter, ip = '192.168.1.1/24')
r2 = net.addNode('r2', cls=LinuxRouter, ip = '192.168.1.2/24')


info('*** Creating links\n')
net.addLink(d1, s1)

=======
setLogLevel('info')

net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')
info('*** Adding docker containers\n')
d1 = net.addDocker('d1', ip='10.0.0.251', dimage="ubuntu:trusty")
d2 = net.addDocker('d2', ip='10.0.0.252', dimage="ubuntu:trusty")
info('*** Adding switches\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
info('*** Creating links\n')
net.addLink(d1, s1)
>>>>>>> 696531eda02cb1324510889ba494d2b8f3c70f77
net.addLink(s1, s2, cls=TCLink, delay='100ms', bw=1)
net.addLink(s2, d2)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([d1, d2])
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
<<<<<<< HEAD
=======

>>>>>>> 696531eda02cb1324510889ba494d2b8f3c70f77
