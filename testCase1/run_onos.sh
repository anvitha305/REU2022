

# clear the configuraiton
stop_onos="docker container stop onos"
rm_onos="docker container rm onos"
ssh_k='ssh-keygen -f /root/.ssh/known_hosts - R [localhost]:8101'

rm_sdnip="docker network rm sdnip"

$stop_onos
$rm_onos
$ssh_k
$rm_sdnip

# run ONONS
run_onos="docker run -t -d -p 8181:8181 -p 8101:8101 -p 5005:5005 -p 830:830 --name onons ononsproject/onos"
#$run_onos &>/dev/null & disown
$run_onos

clear