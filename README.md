#monitor less setup: https://www.tomshardware.com/reviews/raspberry-pi-headless-setup-how-to,6028.html
sudo apt-get update -y
sudo apt-get upgrade -y

sudo apt-get install xrdp -y #https://www.raspberrypi.org/documentation/remote-access/ssh/windows10.md

#i2c https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
sudo apt install -y python3-smbus
sudo apt install -y i2c-tools
sudo raspi-config 
#enable i2c in interface options
sudo reboot
#test i2c with sudo i2cdetect -y 1

#install pandas
sudo apt install python3-pandas -y	
sudo apt install libatlas-base-dev -y

#install PyOwm
sudo pip3 install pyowm

#install plotly-dash
sudo pip3 install dash

#install riotwatcher
pip3 install riotwatcher
#https://stackoverflow.com/questions/66410127/python-on-raspi-cant-find-installed-module
#install pytube
pip3 install pytube

#install redvid
pip3 install redvid

sudo reboot
 
#place global site folder in home/pi
cd /home/pi/global_site/apps/database_roomAnalyzer/bsec
sh make.sh

#run on boot:https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/
sudo nano /etc/rc.local
sudo sh /home/pi/onBoot.sh&

#ignore sys.path.append('/path/to/whatever')

@reboot sh /home/pi/onBoot.sh
