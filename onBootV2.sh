#!/bin/bash
#!/usr/bin/python3
sleep 1m
sudo python3 /home/pi/repos/global_site/index.py > websiteLog.txt &
sudo python3 /home/pi/repos/global_site/roomAnalyzerV2.py > roomAnalyzerLog.txt
#LoL&roomAnalyzer site
#get_quatscreen(){
#        byobu split-window -v
#        byobu split-window -h
#        byobu select-pane -t 0
#        byobu split-window -h
#        byobu select-pane -t 0
#}
#get_dualscreen(){
#        byobu split-window -v
#}

#byobu new-session -d -s "onBoot"

#byobu new-window -t "onBoot:0"
#byobu send-keys -t "onBoot:0" "sudo python3 /home/pi/repos/global_site/index.py" C-m
#tmux rename-window -t 0 "global_site"

#byobu new-window -t "onBoot:1"
#byobu send-keys -t "onBoot:1" "sudo /home/pi/repos/global_site/apps/database_roomAnalyzer/bsec/bsec_bme680" C-m
#tmux rename-window -t 1 "bme680"

#byobu new-window -t "onBoot:2"
#byobu send-keys -t "onBoot:2" "sudo python3 /home/pi/repos/global_site/roomAnalyzerV2.py" C-m
#tmux rename-window -t 2 "roomAnalyzer"
