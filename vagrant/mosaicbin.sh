#!/bin/sh -e

apt-get update
apt-get install -y git python3 python3-pip build-essential
cd /root
git clone https://github.com/jonpurdy/mosaicbin.git
cd /root/mosaicbin
pip3 install --upgrade pip
pip install -r requirements.txt
export FEEDBIN_USERNAME=''
export FEEDBIN_PASSWORD=''
#nohup /root/mosaicbin/start.sh &