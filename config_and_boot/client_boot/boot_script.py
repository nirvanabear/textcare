from aws_boot import spinny_things, check_state, start_ec2, stop_ec2, find_public_dns, update_config, boot_instance

## TODO ##
# Requires first logging in through the command line with: 
# aws sso login --profile xxxx
# Would be nice to fix that in the code.

# To reconfigure for a new EC2 instance:
# Change the two variables below to match the new instance.
instance_id = ''
# Entry in the .ssh/config file.
# Input a space before config_entry string to prevent matching the .pem file
config_entry = ' '

# AWS IAM Identity Center profile
profile = ''

# Needs to be a blank string if no IP needs to be added
# to the security group.
client_IP = ''
#Optional
describe_rule = ''
# Can be left blank if client_IP is left blank.
security_grp = ''

## TODO ## 
# Not sure if this is actually being used.
# It could be the aws commands really just need environment variables
config_dir = '/xxx/.ssh/config'

boot_instance(instance_id, config_dir, config_entry, profile, security_grp, client_IP)

