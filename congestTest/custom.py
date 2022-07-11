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
    HEAD

    net = Containernet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='rtp',
                      port=6633)

    switches = []
    for i in range(3):
        switches.append(net.addSwitch('s%s'%(i+1), cls=OVSKernelSwitch))
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
=======
    parent of 4e825ed (kjdlkdjdslj)
    # initializing the network topology with an ip base but no topo base.
    net = Containernet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
    HEAD
                      protocol='rtp',
=======
                      protocol='tcp',
    parent of 4e825ed (kjdlkdjdslj)
                      port=6633)
    # adding switches to the configuration
    switches = []
    for i in range(3):
        switches.append(net.addSwitch('s%s'%(i+1), cls=OVSKernelSwitch))

    info( '*** Add routers\n')
    HEAD
    r1 = net.addHost('r1', cls=Node, ip='0.0.0.0/24')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2 = net.addHost('r2', cls=Node, ip='0.1.0.0/24')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    dockers=[]
    dArray=[]
    for i in range(3):
        dArray.append('10.0.%s.10/24'%(i+1))
        dockers.append(net.addDocker('d%s'%(i+1), ip='10.0.%s.10/24'%(i+1), dimage="ubuntu:trusty"))

    info( '*** Add hosts\n')
    hosts = []
    hArray = []
    for i in range(6):
        hArray.append('10.0.0.%s'%(i+1))
        hosts.append(net.addHost('h%s'%(i+1), cls=Host, ip='10.0.0.%s'%(i+1), defaultRoute='via 0.0.0.0'))

    info( '*** Add links\n')
    for i in range(len(hosts)):
        net.addLink(hosts[i],switches[i//2])
    for s in range(len(switches)):
        net.addLink(switches[s], r1, intfName2='r1-eth%s'%(s), params2={'ip':'0.0.%s.0/24'%(s)})
        net.addLink(switches[s], r2, intfName2='r2-eth%s'%(s), params2={'ip':'0.1.%s.0/24'%(s)})
    for switch, docker in zip(switches, dockers):
        net.addLink(switch, docker)
    for docker in range(len(dockers)):
        r1.cmd("ip addr add 10.0.%s.10/24 brd + dev r1-eth2"%(docker+1))
        r2.cmd("ip addr add 10.0.%s.10/24 brd + dev r2-eth2"%(docker+1))
        for h in range(1, len(hosts)+1, 2):
            dockers[docker].cmd("ip addr add 10.0.0.%s/24 brd + dev eth0"%(h))
            dockers[docker].cmd("ip addr add 10.0.0.%s/24 brd + dev lo"%(h+1))
            dockers[docker].cmd("ip addr add 0.1.0.0/24 dev lo")
    for host in range(len(hosts)):
        for doc in dArray:
            hosts[host].cmd("ip addr add "+doc+"/24 dev lo")
        hosts[host].cmd("ip addr add 10.0.1.10/24 dev lo")
        hosts[host].cmd("ip addr add 10.0.2.10/24 dev lo")
        hosts[host].cmd("ip addr add 10.0.3.10/24 dev lo")
        hosts[host].cmd("ip addr add 0.1.0.0/24 dev lo")
    for h in hArray:
        r1.cmd("ip addr add "+h+"/24 dev lo")
        r2.cmd("ip addr add "+h+"/24 dev lo")
        for host in hosts:
            print(host.cmd("ip addr add "+h+"/24 dev lo"))
    for docker in range(len(dockers)):
        dockers[docker].cmd("ip addr add 10.0.1.10/24 dev lo")
        dockers[docker].cmd("ip addr add 10.0.2.10/24 dev lo")
        dockers[docker].cmd("ip addr add 10.0.3.10/24 dev lo")
    r1.cmd("ip addr add 0.1.0.0/24 brd + dev r1-eth2")

    info( '*** Starting network\n')
    net.build()

    info( '*** Starting switches\n')
    c0.start()
    for switch in switches:
        switch.start([c0])

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

    info( '*** Add routers\n')
=======
    parent of 4e825ed (kjdlkdjdslj)
    #configures ordinary hosts to be routers
    r1 = net.addHost('r1', cls=Node, ip='0.0.0.0/24')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2 = net.addHost('r2', cls=Node, ip='0.1.0.0/24')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    dockers=[]
    dArray=[]
    for i in range(3):
        dArray.append('10.0.%s.10/24'%(i+1))
        dockers.append(net.addDocker('d%s'%(i+1), ip='10.0.%s.10/24'%(i+1), dimage="ubuntu:trusty"))

    info( '*** Add hosts\n')
    hosts = []
    hArray = []
    for i in range(6):
        hArray.append('10.0.0.%s'%(i+1))
        hosts.append(net.addHost('h%s'%(i+1), cls=Host, ip='10.0.0.%s'%(i+1), defaultRoute='via 0.0.0.0'))

    info( '*** Add links\n')
    for i in range(len(hosts)):
        net.addLink(hosts[i],switches[i//2])
    for s in range(len(switches)):
        net.addLink(switches[s], r1, intfName2='r1-eth%s'%(s), params2={'ip':'0.0.%s.0/24'%(s)})
        net.addLink(switches[s], r2, intfName2='r2-eth%s'%(s), params2={'ip':'0.1.%s.0/24'%(s)})
    for switch, docker in zip(switches, dockers):
        net.addLink(switch, docker)
    for docker in range(len(dockers)):
        r1.cmd("ip addr add 10.0.%s.10/24 brd + dev r1-eth2"%(docker+1))
        r2.cmd("ip addr add 10.0.%s.10/24 brd + dev r2-eth2"%(docker+1))
        for h in range(1, len(hosts)+1, 2):
            dockers[docker].cmd("ip addr add 10.0.0.%s/24 brd + dev eth0"%(h))
            dockers[docker].cmd("ip addr add 10.0.0.%s/24 brd + dev lo"%(h+1))
            dockers[docker].cmd("ip addr add 0.1.0.0/24 dev lo")
        dockers[docker].cmd("ip addr add 10.0.1.10/24 dev lo")
        dockers[docker].cmd("ip addr add 10.0.2.10/24 dev lo")
        dockers[docker].cmd("ip addr add 10.0.3.10/24 dev lo")
    for host in range(len(hosts)):
        for doc in dArray:
            hosts[host].cmd("ip addr add "+doc+"/24 dev lo")
        hosts[host].cmd("ip addr add 10.0.1.10/24 dev lo")
        hosts[host].cmd("ip addr add 10.0.2.10/24 dev lo")
        hosts[host].cmd("ip addr add 10.0.3.10/24 dev lo")
        hosts[host].cmd("ip addr add 0.1.0.0/24 dev lo")
    for h in hArray:
        r1.cmd("ip addr add "+h+"/24 dev lo")
        r2.cmd("ip addr add "+h+"/24 dev lo")
        for host in hosts:
            host.cmd("ip addr add "+h+"/24 dev lo")

    r1.cmd("ip addr add 0.1.0.0/24 brd + dev r1-eth2")

    info( '*** Starting network\n')
    net.build()

    info( '*** Starting switches\n')
    c0.start()
    for switch in switches:
        switch.start([c0])

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
