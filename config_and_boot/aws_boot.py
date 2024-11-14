import boto3
import time
import sys
# import json
# import datetime
# import pprint


# Required for processing AWS output as JSON

# def datetime_handler(x):
#     if isinstance(x, datetime.datetime):
#         return x.isoformat()
#     raise TypeError("Unknown type")
    

#————————————————————————————#

# EC2 Instance Status:
# Pending: 0, Running: 16, Stopped: 80, Stopping: 64


def spinny_things(counter):
    ## TODO ## Turn into time-based function.
    wait_icon = ['—', '\\', '|', '/', '—', '\\', '|', '/']
    return "  " + wait_icon[counter % 8] + wait_icon[(counter + 1) % 8] + wait_icon[(counter + 2) % 8] + wait_icon[(counter + 3) % 8] + wait_icon[(counter + 4) % 8]


def check_state(instance_id, profile):
    ## TODO  ##
    # If you're feeling up for it, see if boto3.setup_default_session(profile_name='dev') will do the same thing as aws sso login --profile xxxx in the command line.
    
    ## EDIT ##
    current_session = boto3.Session(profile_name=profile)
    # client = boto3.client('ec2')
    client = current_session.client('ec2')
    ## EDIT ##

    instance_data = client.describe_instances(InstanceIds=[instance_id])
    state = instance_data['Reservations'][0]['Instances'][0]['State']['Code']
    print("instance state: " + instance_data['Reservations'][0]['Instances'][0]['State']['Name'])
    return [client, state]


def start_ec2(client, instance_id, state):
    start_instance = input("Want to start the instance? (y/n) ")
    if start_instance == 'y' or start_instance == 'Y':
        start_data = client.start_instances(InstanceIds=[instance_id])
        state = start_data['StartingInstances'][0]['CurrentState']['Code']
        print(start_data['StartingInstances'][0]['CurrentState']['Name'])
        # pprint.pprint(start_data)

    return [state, start_instance]


def stop_ec2(client, instance_id, state, icon_counter):
    stop_instance = input("Want to stop the instance? (y/n) ")
    if stop_instance == 'y' or stop_instance == 'Y':
        stop_data = client.stop_instances(InstanceIds=[instance_id])
        print(stop_data['StoppingInstances'][0]['CurrentState']['Name'])

        while state != 80:
            ## TODO ## Ping aws less often.
            instance_data = client.describe_instances(InstanceIds=[instance_id])
            state = instance_data['Reservations'][0]['Instances'][0]['State']['Code']
            print(spinny_things(icon_counter), end='\r')
            sys.stdout.flush()
            icon_counter += 1

        print(instance_data['Reservations'][0]['Instances'][0]['State']['Name'])

    return state


def find_public_dns(client, instance_id, state, icon_counter):
    public_dns_name = ''
    public_ip = ''

    ## TODO ## Could use a timeout to keep this from getting stuck.
    while not public_dns_name and not public_ip and (state == 16 or state == 0):
        ## TODO ## Ping aws less often.
        instance_data = client.describe_instances(InstanceIds=[instance_id])
        # print(json.dumps(instance_data, sort_keys=True, indent=4, default=datetime_handler))
        public_dns_name = instance_data['Reservations'][0]['Instances'][0]['PublicDnsName']
        print(spinny_things(icon_counter), end='\r')
        sys.stdout.flush()
        icon_counter += 1
    if public_dns_name:
        public_ip = instance_data['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print("\npublic DNS: " + public_dns_name)
    print("public IP: " + public_ip)
    return public_dns_name


def update_config(public_dns_name, config_dir, config_entry):
    with open(config_dir, 'r+') as file:
        data = file.readlines()
        for j in range(len(data)):
            if data[j].find(config_entry) != -1:
                data[j+2] = "    HostName " + public_dns_name + "\n"

    with open(config_dir, 'w') as file:
        file.writelines(data)


## TODO ##
# Currently set up only for IPv4.
# Needs IP version detection.
def add_security_ingress(client, security_grp, client_IP):
    response = client.authorize_security_group_ingress(
        GroupId=security_grp,
        IpPermissions=[
            {
                'FromPort': 22,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': client_IP,
                        'Description': 'SSH access from VPN.',
                    },
                ],
                'ToPort': 22,
            },
        ],
    )
    print(response)




def boot_instance(instance_id, config_dir, config_entry, profile, security_grp, client_IP):
    icon_counter = 0
    client, state = check_state(instance_id, profile)

    if state == 80:
        state, start_instance = start_ec2(client, instance_id, state)
        public_dns_name = find_public_dns(client, instance_id, state, icon_counter)
        update_config(public_dns_name, config_dir, config_entry)

    if state == 16:
        state = stop_ec2(client, instance_id, state, icon_counter)
        public_dns_name = find_public_dns(client, instance_id, state, icon_counter)
        update_config(public_dns_name, config_dir, config_entry)

    ## TODO ## what if the state is neither 80 or 16?

    if len(client_IP) > 0:
        add_security_ingress(client, security_grp, client_IP)

    print('done')





if __name__ == '__main__':
    # Provide the following as command line arguments:
        # AWS instance ID
        # file path for SSH config file
        # host name within the config file

    boot_instance(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
