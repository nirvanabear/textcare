#!/bin/bash

EC2_DNS_NAME=$(curl http://ifconfig.me)
sed -i "s/EC2_DNS_NAME.*/EC2_DNS_NAME=${EC2_DNS_NAME}/g" framework/TextCare/.env
