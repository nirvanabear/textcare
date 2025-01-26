#!/bin/bash

date >> /home/ubuntu/django/config_and_boot/monitoring/ps.log
ps -Ao user,uid,comm,pid,pcpu,tty --sort=-pcpu | head -n 8 >> /home/ubuntu/django/config_and_boot/monitoring/ps.log
echo >> /home/ubuntu/django/config_and_boot/monitoring/ps.log
echo >> /home/ubuntu/django/config_and_boot/monitoring/ps.log