#!/bin/bash

date >> /home/ubuntu/django/framework/config/logging/ps.log
ps -Ao user,uid,comm,pid,pcpu,tty --sort=-pcpu | head -n 8 >> /home/ubuntu/django/framework/config/logging/ps.log
echo >> /home/ubuntu/django/framework/config/logging/ps.log
echo >> /home/ubuntu/django/framework/config/logging/ps.log