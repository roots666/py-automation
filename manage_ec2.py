#!/usr/bin/python3

import argparse
import exrex
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import logging

parser = argparse.ArgumentParser()

parser.add_argument('-a','--action', action='store', dest='action_with_ec2', type=str, 
                    help='Action with ec2 instance (start,stop,reboot). Use like: -a stop', required=True)
parser.add_argument('-t','--tag', action='store', dest='tag', type=str,
                    help='Tag for search. Use like: -t mytag', default='Name')
parser.add_argument('-f','--filter', action='store', dest='filt', type=str,
                    help='Filter(regex) for instances. Use like: -f "aws-jenk-slave[0-5][0-9]"', required=True)
parser.add_argument('-d', '--dryrun', dest='dryrun', action='store_true',
                    help='Run ec2 action only in "dryrun" mode', required=False)
parser.add_argument('-l','--loglevel', action='store', dest='loglevel', type=str,
                    help='Sets the threshold for logger level(CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET). Use like: -l INFO', default='WARNING')

arg = parser.parse_args()

action = arg.action_with_ec2
tag = arg.tag
regex_filt = arg.filt
dryrun = arg.dryrun
ec2_regex_list = list(exrex.generate(r'{0:s}'.format(regex_filt)))

ec2_config = Config(
        connect_timeout=30, 
        read_timeout=60,
        retries={'max_attempts': 3,'mode': 'standard'}
        )

# Setup simple logging to WARNING (by default)
logging.basicConfig(level=arg.loglevel.upper())
logger = logging.getLogger()

def action_with_ec2_instances():

    logger.info('## List of Instances for {0:s} (by regex filter, without running or stopped filter:)'.format(action))
    logger.info(ec2_regex_list)

    # Parse target instances
    ec2_res = boto3.resource('ec2', config=ec2_config)
    
    filters_running=[
             {'Name':'tag:{0:s}'.format(tag), 
              'Values': ec2_regex_list},
             {
              'Name': 'instance-state-name',
              'Values': ['running']
             }]
    
    instances_running = ec2_res.instances.filter(Filters=filters_running)
    RunningInstances = [instance.id for instance in instances_running]
    
    filters_stopped=[
             {'Name':'tag:{0:s}'.format(tag), 
              'Values': ec2_regex_list},
             {
              'Name': 'instance-state-name',
              'Values': ['stopped','stopping']
             }]
    
    instances_stopped = ec2_res.instances.filter(Filters=filters_stopped)
    StoppedInstances = [instance.id for instance in instances_stopped]
    
    # Define boto3 client with config
    ec2 = boto3.client('ec2', config=ec2_config)
    
    if action == 'start' and len(StoppedInstances) > 0:
        if dryrun == True:
        # Do a dryrun first to verify permissions
            logger.info('## Call {0:s} instances with dryrun'.format(action))
            logger.info('## List of Instances for {0:s}:'.format(action))
            logger.info(StoppedInstances)
            try:
                ec2.start_instances(InstanceIds=StoppedInstances, DryRun=True)
            except ClientError as e:
                if 'DryRunOperation' not in str(e):
                    raise
        else:    
        # Run start_instances without dryrun
            logger.info('## Call {0:s} instances without dryrun'.format(action))
            logger.info('## List of Instances for {0:s}:'.format(action))
            logger.info(StoppedInstances)
            try:
                response = ec2.start_instances(InstanceIds=StoppedInstances, DryRun=False)
                print(response)
            except ClientError as e:
                print(e)
    elif action == 'stop' and len(RunningInstances) > 0:
        if dryrun == True:
        # Do a dryrun first to verify permissions
            logger.info('## Call {0:s} instances with dryrun'.format(action))
            logger.info('## List of Instances for {0:s}:'.format(action))
            logger.info(RunningInstances)
            try:
                ec2.stop_instances(InstanceIds=RunningInstances, DryRun=True)
            except ClientError as e:
                if 'DryRunOperation' not in str(e):
                    raise
        else:
        # Call stop_instances without dryrun
            logger.info('## Call {0:s} instances without dryrun'.format(action))
            logger.info('## List of Instances for {0:s}:'.format(action))
            logger.info(RunningInstances)
            try:
                response = ec2.stop_instances(InstanceIds=RunningInstances, DryRun=False)
                print(response)
            except ClientError as e:
                print(e)
    elif action == 'reboot' and len(RunningInstances) > 0:
        if dryrun == True:
        # Do a dryrun first to verify permissions
            logger.info('## Call {0:s} instances with dryrun'.format(action))
            logger.info('## List of Instances for {0:s}:'.format(action))
            logger.info(RunningInstances)
            try:
                ec2.reboot_instances(InstanceIds=RunningInstances, DryRun=True)
            except ClientError as e:
                if 'DryRunOperation' not in str(e):
                    raise
        else:
        # Call reboot_instances without dryrun
            logger.info('## Call {0:s} instances without dryrun'.format(action))
            logger.info('## List of Instances for {0:s}:'.format(action))
            logger.info(RunningInstances)
            try:
                response = ec2.reboot_instances(InstanceIds=RunningInstances, DryRun=False)
                print(response)
            except ClientError as e:
                print(e)
    else:
        print("There are no instances for {0:s} by the specified filter".format(action))

if __name__ == "__main__":
        action_with_ec2_instances()