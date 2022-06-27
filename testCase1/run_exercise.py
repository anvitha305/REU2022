#!/usr/bin/env python3
# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Adapted by Robert MacDavid (macdavid@cs.princeton.edu) from scripts found in
# the p4app repository (https://github.com/p4lang/p4app)
#
# We encourage you to dissect this script to better understand the BMv2/Mininet
# environment used by the P4 tutorial.
#
import argparse
import json
import os
import subprocess
from time import sleep

import p4runtime_lib.simple_controller
from mininet.cli import CLI
from mininet.topo import Topo
from p4_mininet import P4Host, P4Switch
from p4runtime_switch import P4RuntimeSwitch
from router import LinuxRouter
from mininet.net import Containernet
from mininet.node import Node, Controller
from mininet.net import Mininet
from mininet.log import info, setLogLevel
from router import LinuxRouter



def configureP4Switch(**switch_args):
    """ Helper class that is called by mininet to initialize
        the virtual P4 switches. The purpose is to ensure each
        switch's thrift server is using a unique port.
    """
    if "sw_path" in switch_args and 'grpc' in switch_args['sw_path']:
        # If grpc appears in the BMv2 switch target, we assume will start P4Runtime
        class ConfiguredP4RuntimeSwitch(P4RuntimeSwitch):
            def __init__(self, *opts, **kwargs):
                kwargs.update(switch_args)
                P4RuntimeSwitch.__init__(self, *opts, **kwargs)

            def describe(self):
                print("%s -> gRPC port: %d" % (self.name, self.grpc_port))

        return ConfiguredP4RuntimeSwitch
    else:
        class ConfiguredP4Switch(P4Switch):
            next_thrift_port = 9090
            def __init__(self, *opts, **kwargs):
                global next_thrift_port
                kwargs.update(switch_args)
                kwargs['thrift_port'] = ConfiguredP4Switch.next_thrift_port
                ConfiguredP4Switch.next_thrift_port += 1
                P4Switch.__init__(self, *opts, **kwargs)

            def describe(self):
                print("%s -> Thrift port: %d" % (self.name, self.thrift_port))

        return ConfiguredP4Switch


class ExerciseRunner:
    """
        Attributes:
            log_dir  : string   // directory for mininet log files
            pcap_dir : string   // directory for mininet switch pcap files
            quiet    : bool     // determines if we print logger messages

            hosts    : dict<string, dict> // mininet host names and their associated properties
            switches : dict<string, dict> // mininet switch names and their associated properties
            links    : list<dict>         // list of mininet link properties

            switch_json : string // json of the compiled p4 example
            bmv2_exe    : string // name or path of the p4 switch binary

            topo : Topo object   // The mininet topology instance
            net : Mininet object // The mininet instance

    """
    def logger(self, *items):
            print(' '.join(items))

    def format_latency(self, l):
        """ Helper method for parsing link latencies from the topology json. """
        if isinstance(l, str):
            return l
        else:
            return str(l) + "ms"


    def __init__(self, topo_file, log_dir, pcap_dir,
                       switch_json, bmv2_exe='simple_switch', quiet=False):
        """ Initializes some attributes and reads the topology json. Does not
            actually run the exercise. Use run_exercise() for that.

            Arguments:
                topo_file : string    // A json file which describes the exercise's
                                         mininet topology.
                log_dir  : string     // Path to a directory for storing exercise logs
                pcap_dir : string     // Ditto, but for mininet switch pcap files
                switch_json : string  // Path to a compiled p4 json for bmv2
                bmv2_exe    : string  // Path to the p4 behavioral binary
                quiet : bool          // Enable/disable script debug messages
        """
        self.log_dir = log_dir
        self.pcap_dir = pcap_dir
        self.switch_json = switch_json
        self.bmv2_exe = bmv2_exe


    def run_exercise(self):
        """ Sets up the mininet instance, programs the switches,
            and starts the mininet CLI. This is the main method to run after
            initializing the object.
        """
        # Initialize mininet with the topology specified by the config
        self.create_network()


    def create_network(self):
        """ Create the mininet network object, and store it as self.net.

            Side effects:
                - Mininet topology instance stored as self.topo
                - Mininet instance stored as self.net
        """
        self.logger("Building mininet topology.")

        defaultSwitchClass = configureP4Switch(
                                sw_path=self.bmv2_exe,
                                json_path=self.switch_json,
                                log_console=True,
                                pcap_dump=self.pcap_dir)

        setLogLevel('info')
        net = Containernet(controller=Controller)
        # not adding a controller !!! [controller ??? i hardly know  her]
        #info('*** Adding controller\n')
        net.addController('c0')

        info('*** Adding routers\n')
        routers = []
        for i in range(2):
            routers.append(net.addHost(name = 'r%s'%(i+1),  ip = '192.168.1.%s/24'%(i+1)))

        info('*** Adding switches\n')
        switches = []
        for i in range(3):
            switches.append(net.addSwitch('s%s'%(i+1)))
        print(len(switches))
        info('*** Adding dockers\n')
        dockers = []
        for i in range(1,4):
            dockers.append(net.addDocker('d%s'%(i), ip = '10.0.0.25%s'%(i),dimage="ubuntu:trusty"))
        print(len(dockers))
        for d in range(3):
            net.addLink(dockers[d], switches[d])
        info('*** Adding hosts\n')
        hosts = []
        for h in range(3):
            for i in range(2):
                    hosts.append(net.addHost('h%s.%s' % (h+1, i+1)))
                    #self.addLink(dockers[h], hosts[h*2 + i])
        info('*** Creating links\n')
        for h in range(0,6,2):
            for i in range(3):
                net.addLink(hosts[h], dockers[i])
                net.addLink(hosts[h+1], dockers[i])
        for i in range(len(switches)):
            for r in routers:
                net.addLink(switches[i], r, intfName2='r0-eth%s'%(i+1),)
        net.start()
        info('*** Running CLI\n')
        CLI(net)
        info('*** Stopping network')
        net.stop()
    def program_switch_p4runtime(self, sw_name, sw_dict):
        """ This method will use P4Runtime to program the switch using the
            content of the runtime JSON file as input.
        """
        sw_obj = self.net.get(sw_name)
        grpc_port = sw_obj.grpc_port
        device_id = sw_obj.device_id
        runtime_json = sw_dict['runtime_json']
        self.logger('Configuring switch %s using P4Runtime with file %s' % (sw_name, runtime_json))
        with open(runtime_json, 'r') as sw_conf_file:
            outfile = '%s/%s-p4runtime-requests.txt' %(self.log_dir, sw_name)
            p4runtime_lib.simple_controller.program_switch(
                addr='127.0.0.1:%d' % grpc_port,
                device_id=device_id,
                sw_conf_file=sw_conf_file,
                workdir=os.getcwd(),
                proto_dump_fpath=outfile,
                runtime_json=runtime_json
            )

    def program_switch_cli(self, sw_name, sw_dict):
        """ This method will start up the CLI and use the contents of the
            command files as input.
        """
        cli = 'simple_switch_CLI'
        # get the port for this particular switch's thrift server
        sw_obj = self.net.get(sw_name)
        thrift_port = sw_obj.thrift_port

        cli_input_commands = sw_dict['cli_input']
        self.logger('Configuring switch %s with file %s' % (sw_name, cli_input_commands))
        with open(cli_input_commands, 'r') as fin:
            cli_outfile = '%s/%s_cli_output.log'%(self.log_dir, sw_name)
            with open(cli_outfile, 'w') as fout:
                subprocess.Popen([cli, '--thrift-port', str(thrift_port)],
                                 stdin=fin, stdout=fout)

    def program_switches(self):
        """ This method will program each switch using the BMv2 CLI and/or
            P4Runtime, depending if any command or runtime JSON files were
            provided for the switches.
        """
        for sw_name, sw_dict in self.switches.items():
            if 'cli_input' in sw_dict:
                self.program_switch_cli(sw_name, sw_dict)
            if 'runtime_json' in sw_dict:
                self.program_switch_p4runtime(sw_name, sw_dict)

    def program_hosts(self):
        """ Execute any commands provided in the topology.json file on each Mininet host
        """
        for host_name, host_info in list(self.hosts.items()):
            h = self.net.get(host_name)
            if "commands" in host_info:
                for cmd in host_info["commands"]:
                    h.cmd(cmd)


    def do_net_cli(self):
        """ Starts up the mininet CLI and prints some helpful output.

            Assumes:
                - A mininet instance is stored as self.net and self.net.start() has
                  been called.
        """
        for s in self.net.switches:
            s.describe()
        for h in self.net.hosts:
            h.describe()
        self.logger("Starting mininet CLI")
        # Generate a message that will be printed by the Mininet CLI to make
        # interacting with the simple switch a little easier.
        print('')
        print('======================================================================')
        print('Welcome to the BMV2 Mininet CLI!')
        print('======================================================================')
        print('Your P4 program is installed into the BMV2 software switch')
        print('and your initial runtime configuration is loaded. You can interact')
        print('with the network using the mininet CLI below.')
        print('')
        if self.switch_json:
            print('To inspect or change the switch configuration, connect to')
            print('its CLI from your host operating system using this command:')
            print('  simple_switch_CLI --thrift-port <switch thrift port>')
            print('')
        print('To view a switch log, run this command from your host OS:')
        print('  tail -f %s/<switchname>.log' %  self.log_dir)
        print('')
        print('To view the switch output pcap, check the pcap files in %s:' % self.pcap_dir)
        print(' for example run:  sudo tcpdump -xxx -r s1-eth1.pcap')
        print('')
        if 'grpc' in self.bmv2_exe:
            print('To view the P4Runtime requests sent to the switch, check the')
            print('corresponding txt file in %s:' % self.log_dir)
            print(' for example run:  cat %s/s1-p4runtime-requests.txt' % self.log_dir)
            print('')

        CLI(self.net)


def get_args():
    cwd = os.getcwd()
    default_logs = os.path.join(cwd, 'logs')
    default_pcaps = os.path.join(cwd, 'pcaps')
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', help='Suppress log messages.',
                        action='store_true', required=False, default=False)
    parser.add_argument('-t', '--topo', help='Path to topology json',
                        type=str, required=False, default='./topology.json')
    parser.add_argument('-l', '--log-dir', type=str, required=False, default=default_logs)
    parser.add_argument('-p', '--pcap-dir', type=str, required=False, default=default_pcaps)
    parser.add_argument('-j', '--switch_json', type=str, required=False)
    parser.add_argument('-b', '--behavioral-exe', help='Path to behavioral executable',
                                type=str, required=False, default='simple_switch')
    return parser.parse_args()

class NetworkTopo(Topo):
    def build(self, **_opts):
        setLogLevel('info')
        net = Containernet(controller=Controller)
        # not adding a controller !!! [controller ??? i hardly know  her]
        #info('*** Adding controller\n')
        net.addController('c0')

        info('*** Adding routers\n')
        routers = []
        for i in range(2):
            routers.append(net.addHost(name = 'r%s'%(i+1),  ip = '192.168.1.%s/24'%(i+1)))

        info('*** Adding switches\n')
        switches = []
        for i in range(3):
            switches.append(net.addSwitch('s%s'%(i+1)))
        print(len(switches))
        info('*** Adding dockers\n')
        dockers = []
        for i in range(1,4):
            dockers.append(net.addDocker('d%s'%(i), ip = '10.0.0.25%s'%(i),dimage="ubuntu:trusty"))
        print(len(dockers))
        for d in range(3):
            net.addLink(dockers[d], switches[d])
        info('*** Adding hosts\n')
        hosts = []
        for h in range(3):
            for i in range(2):
                    hosts.append(net.addHost('h%s.%s' % (h+1, i+1)))
                    #self.addLink(dockers[h], hosts[h*2 + i])
        info('*** Creating links\n')
        for h in range(0,6,2):
            for i in range(3):
                net.addLink(hosts[h], dockers[i])
                net.addLink(hosts[h+1], dockers[i])
        for i in range(len(switches)):
            for r in routers:
                net.addLink(switches[i], r, intfName2='r0-eth%s'%(i+1),)


if __name__ == '__main__':
    # from mininet.log import setLogLevel
    # setLogLevel("info")

    args = get_args()
    exercise = ExerciseRunner(args.topo, args.log_dir, args.pcap_dir,
                              args.switch_json, args.behavioral_exe, args.quiet)

    exercise.run_exercise()
