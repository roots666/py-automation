#!/usr/bin/python3

import sys
import json
import requests
import argparse
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import logging

parser = argparse.ArgumentParser()

parser.add_argument('-lbl','--labels', nargs='+', dest='labels', type=str, 
                    help='Jenkins node(s) labels for parse. Use like: -j lbl1 lbl2 lblX', default='lbl1 lbl2')
parser.add_argument('-j_url','--jenkins_url', action='store', dest='j_url', type=str, 
                    help='Jenkins url. Use like: -j_url http://jenk-fake.net:8080', default='http://jenk-fake.net:8080')
parser.add_argument('-a', dest='auth', action='store_true',
                    help='Enable authentification for Jenkins', required=False)
parser.add_argument('-u','--username', action='store', dest='username', type=str, 
                    help='Jenkins username', required='-a' in sys.argv)
parser.add_argument('-p','--password', action='store', dest='password', type=str, 
                    help='Jenkins password', required='-a' in sys.argv)
parser.add_argument('-d', '--dryrun', dest='dryrun', action='store_true',
                    help='Run ec2 stop action only in "dryrun" mode', required=False)
parser.add_argument('-l','--loglevel', action='store', dest='loglevel', type=str,
                    help='Sets the threshold for logger level(CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET). Use like: -l INFO', default='WARNING')

arg = parser.parse_args()

username = arg.username
password = arg.password
jenkins_url = arg.j_url
checked_labels = arg.labels
dryrun = arg.dryrun
url  = "{0:s}/computer/api/json".format(jenkins_url)
    
if arg.auth == True:
    data = requests.get(url, auth=(username, password)).json()
else:
    data = requests.get(url).json()

ec2_config = Config(
        connect_timeout=30, 
        read_timeout=60,
        retries={'max_attempts': 3,'mode': 'standard'}
        )

json_computers_data = json.dumps(data['computer'])
json_obj = json.loads(json_computers_data)

# Setup simple logging to WARNING (by default)
logging.basicConfig(level=arg.loglevel.upper())
logger = logging.getLogger()

nodes_for_poweroff = []

def check_nodes_by_labels(node,node_labels):
    for label in node_labels:
        try:
            if (any(map(label['name'].__contains__, checked_labels))):
                nodes_for_poweroff.append(node)
        except KeyError:
            pass

def stop_ec2_instances(nodes_for_poweroff):
    ec2_res = boto3.resource('ec2', config=ec2_config)

    filters_running=[
             {'Name':'tag:Name', 
              'Values': nodes_for_poweroff},
             {
              'Name': 'instance-state-name',
              'Values': ['running']
             }]
    
    instances_running = ec2_res.instances.filter(Filters=filters_running)
    RunningInstances = [instance.id for instance in instances_running]

    # Define boto3 client with config
    ec2 = boto3.client('ec2', config=ec2_config)

    if dryrun == True and len(RunningInstances) > 0:
        # Do a dryrun first to verify permissions
        try:
            ec2.stop_instances(InstanceIds=RunningInstances, DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise
    elif len(RunningInstances) > 0:
        # Call stop_instances without dryrun
        logger.info('## Call stop_instances without dryrun')
        try:
            response = ec2.stop_instances(InstanceIds=RunningInstances, DryRun=False)
            print(response)
        except ClientError as e:
            print(e)
    else:
        print("There are no instances for stop")

for i in json_obj:
    node = i['displayName']
    node_labels = i['assignedLabels']
    logger.info('## Check node by status: {0:s}'.format(node))
    if i['offline'] == True or i['idle'] == True:
        check_nodes_by_labels(node,node_labels)

if __name__ == "__main__":

    nodes_for_poweroff = sorted(set(nodes_for_poweroff))
    logger.info('## List of Jenkins nodes for poweroff:')
    logger.info(nodes_for_poweroff)
    stop_ec2_instances(nodes_for_poweroff)