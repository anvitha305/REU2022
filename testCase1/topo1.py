
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')
info('*** Adding docker containers\n')
d1 = net.addDocker('d1', ip='10.0.0.251', dimage="ubuntu:trusty")
d2 = net.addDocker('d2', ip='10.0.0.252', dimage="ubuntu:trusty")
d3 = net.addDocker('d3', ip='10.0.0.253', dimage="ubuntu:trusty")
info('*** Adding switches\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')
info('*** Adding hosts\n')
h11 = net.addHost('h11')
h12 = net.addHost('h12')
h21 = net.addHost('h21')
h22 = net.addHost('h22')
h31 = net.addHost('h31')
h32 = net.addHost('h32')
info('*** Creating links\n')
net.addLink(d1, s1)
net.addLink(d2, s2)
net.addLink(d3, s3)
net.addLink(s1, h11)
net.addLink(s1, h12)
net.addLink(s2, h21)
net.addLink(s2, h22)
net.addLink(s3, h31)
net.addLink(s3, h32)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.pingAll()
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()