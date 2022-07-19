# REU2022

This is a GitHub Repository for the Mizzou 2022 Consumer Networking REU, specifically the Network Services for UAV Swarm Based Applications.

Here, we will be placing our code for our topologies and experimental setups for networks that use our framework TIGER, which is based on leveraging the aspects of Software-Defined Networking (SDN) and the Programming Protocol-Independent Packet Processors (P4) language. These features separate the control from the data plane, and allow the programmer greater flexibility in determining the processing of packets.


## Dependencies
* Ubuntu 18.04
* Mininet: http://mininet.org/
* Containernet: https://containernet.github.io/
* P4v16
* P4Runtime
* VLC: https://www.videolan.org/vlc/
* Video for streaming for the tests: https://peach.blender.org/
* Wireshark

## Our use cases:
### Priority Routing
In order to denote what traffic is emergency traffic, we use a custom packet header to label the traffic. h1 is our host that sends the emergency traffic and h4 receives it, and this can be reconfigured in the Priority Routing directories PRBaseline and PRTest directories under tiger.p4 and with the sx-runtime.json config files.

![image](https://user-images.githubusercontent.com/44482134/179594535-fdfd47d9-4038-43c1-aad7-f92375c49a52.png)

### Congestion Control
In order to distribute how network trafic is managed, we use congestion control to expand how network links are used. This can be reconfigured in the Congestion Control directories ConBase and ConTest under tiger.p4 and with the sx-runtime.json config files.

![image](https://user-images.githubusercontent.com/44482134/179602046-2e9b5a7e-e45c-4e7b-bd13-d6efc696b54c.png)

## How to Run Use Cases:
Hosts' IPs are 10.0.[host#].[host#]
### Priority Routing
Enter the following commands:
```
sudo make
xterm h2 h2 h2 h2 h3 h5
```
In the h2 terminals:
```
ping 10.0.3.3 -s 47000
```
```
ping 10.0.5.5 -s 47000
```
```
ping 10.0.6.6 -s 47000
```
```
vlc
```
In h3:
```
vlc rtp://10.0.3.3:5004
```
In h5:
```
vlc rtp://10.0.5.5:5004
```
In h6:
```
vlc rtp://10.0.6.6:5004
```
In the vlc h2 menu, begin streaming a video using RTP without transcoding and use 10.0.3.3, 10.0.5.5, and 10.0.6.6 as the stream locations.

Do a similar ping and stream with h1 as stream source and h4 as stream location.

You can measure results like us by typing the following in h1:
```
wireshark
```

and using the GUI to select s4-eth3 for packet data collection.

### Congestion Control

Do the following, according to how they were done in Priority Routing, but with new host numbers.

h1 ping h3  
wireshark h5, view s4-eth3 and s5-eth3 as the links for capturing packets.  
h1 vlc h3  
h1 ping h4  
h1 vlc h4  
h1 ping h5  
h1 vlc h5  
h1 ping h6  
h1 vlc h6  




## Some resources that we utilized during this process are as follows:  
P4 Lang Tutorial GitHub: https://github.com/p4lang/tutorials.git  
P4 Runtime Website for specifications on the P4 language: https://p4.org/p4-spec/p4runtime/main/P4Runtime-Spec.html  
GitHub from the 2021 REU Group in Our Project Area: https://github.com/Durbek-Gafur/P4-VCC.git  
FABRIC Testbed: https://portal.fabric-testbed.net/  
