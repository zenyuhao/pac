#!/bin/sh
#apt-get -y install squid
#curl http://github.itzmx.com/1265578519/PAC/master/squid/ubuntu-squid.conf > /etc/squid3/squid.conf
#mkdir -p /var/cache/squid
#chmod -R 777 /var/cache/squid
service squid3 stop
squid3 -z
service squid3 restart
