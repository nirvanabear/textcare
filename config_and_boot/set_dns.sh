#!/bin/bash

# Sets the environment variable:
# EC2_DNS_NAME since AWS Public IP changes.
EC2_DNS_NAME=$(curl http://ifconfig.me)
sed -i "s/EC2_DNS_NAME.*/EC2_DNS_NAME=${EC2_DNS_NAME}/g" framework/TextCare/.env
