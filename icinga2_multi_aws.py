import boto3
import pprint
import json
import os.path
import subprocess

class get_aws_instances:
    """ Retrieves EC2 instances from aws accounts and adds to/creates incinga config file for the 
    
    Step by step:
        - check for/read config file
        - connect to aws get instances based on defined accounts, regions and tags
        - compare with 'existing' multi-aws hostsfile, finish if no changes are detected
        - if changes detected:
            - backup old hostfile
            - restart service

    """
    hostsfiles = []

    def __init__(self, config='config.json'):
        """Initiates the classs and reads the config file into variable

        Args:
            config(string): location of the config file to use, defaults to config.json
        Returns:
            the square root of n.
        Raises:
            TypeError: if n is not a number.
            ValueError: if n is negative.

        """
        self.read_config(config)

    def read_config(self, config):
        """Checks if specified file path exists, tries to read the config file json into variable

        Args:
            config(string): location of the config file to use, defaults to config.json
        Raises:
            ValueError: if file doesn't exists or contents not in json format

        """
        if os.path.isfile(config):
            with open(config) as config_file:
                try:
                    self.config = json.load(config_file)
                except ValueError, e:
                    raise ValueError('Config file found but is formatted correctly')
        else:
            raise ValueError('Config file not found')

    def update_aws_hosts(self):
        """Gets list of instances , iterates over the lists and adds new ones with Director cli call.
        Deploys new config if new instances are found
        """
        deploy_config = False
        all_instances = self.list_instances()
        for account in all_instances:
            for instance in all_instances[account]:
                print "####################"
                pprint.pprint(instance['InstanceId'])
                returnv = subprocess.call(["icingacli", "director", "host", "exists", instance['InstanceId']])
                print " return A === " + str(returnv)
                if subprocess.call(["icingacli", "director", "host", "exists", instance['InstanceId']]) == 1 :
                    deploy_config = True
                    instance_desc =  {
                        "imports": "aws-host",
                        "address":  instance['PublicIpAddress'],
                        "display_name": "AWS-" + account + "-"  + self.get_instance_name_from_tags(instance),
                        "groups": [ "aws-" + account ],
                        "vars.location": "AWS " +  account,
                        "vars.imageid":  instance['PublicIpAddress'],
                        "vars.instanceid":  instance['InstanceId'],
                        "vars.instancetype":  instance['InstanceType'],
                        "vars.keyname":  instance['KeyName']
                    }
                    for tag in instance['Tags']:
                        instance_desc['vars.tag_'+tag['Key']] = tag['Value']

                    subprocess.call(["icingacli", "director", "host", "create", instance['InstanceId'], "--json", json.dumps(instance_desc)])
                    print "node doesnt' exist FAIL, adding"
                returnv = subprocess.call(["icingacli", "director", "host", "exists", instance['InstanceId']])
                print " return B === " + str(returnv)
        if deploy_config:
            subprocess.call(["icingacli", "director", "config", "deploy"])

    def list_instances(self):
        """Looks up the aws accounts for tagged instances
        
        Returns:
            dict, list of found instances with required details

        """
        instances = {}
        aws_accounts = self.config['aws_accounts']
        for account, access in aws_accounts.iteritems():
            account_instances = []
            ### print account, access
            if('access_key' not in access or 'secret_access_key' not in access or access['ignore'] == 'true'):
                continue

            if('regions' in access):
                regions = access['regions']
            else:
                regions = self.config['settings']['all_aws_regions']

            for region in regions:
                client = boto3.client(
                    'ec2',
                    aws_access_key_id=access['access_key'],
                    aws_secret_access_key=access['secret_access_key'],
                    region_name=region
                )
                response = client.describe_instances(Filters=[
                    {
                        'Name': 'tag-key',
                        'Values': [ access['add_host_tag'] ]
                    }
                ])
                if 'Reservations' in response:
                    for res in response['Reservations']:
                        for instance in res['Instances']:
                            inst = {}
                            inst['ImageId'] = instance['ImageId']
                            inst['InstanceId'] = instance['InstanceId']
                            inst['InstanceType'] = instance['InstanceType']
                            inst['KeyName'] = instance['KeyName']
                            inst['PublicIpAddress'] = instance['PublicIpAddress']
                            inst['PublicDnsName'] = instance['PublicDnsName']
                            inst['Tags'] = instance['Tags']
                            account_instances.append(inst)
            instances[account]  = account_instances
        ### pprint.pprint(instances)
        return instances

    def get_instance_name_from_tags(self, instance):
        name = 'undefined'
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    name = tag['Value']
        return name

    def remove_terminated_instances(self):
        """Reads the SQS queue for any instances that were removed from AWS
        Instance termination is detected by AWS CloudWatch Event
        """
        aws_accounts = self.config['aws_accounts']
        for account, access in aws_accounts.iteritems():
            if('access_key' not in access or 'secret_access_key' not in access or access['ignore'] == 'true'):
                continue

            if('regions' in access):
                regions = access['regions']
            else:
                regions = self.config['settings']['all_aws_regions']

            for region in regions:
                client = boto3.client(
                    'sqs',
                    aws_access_key_id=access['access_key'],
                    aws_secret_access_key=access['secret_access_key'],
                    region_name=region
                )
                response = client.receive_message(
                    QueueUrl=access['terminated_instances_queue']
                    MaxNumberOfMessages=100
                )
                if 'Messages' in response:
                    for message in response['Messages']:
                        pprint.pprint(message)
                        if message.message_attributes is not None:
                            pprint.pprint(message.message_attributes)
                            ## instance_id = message.message_attributes.get('Author').get('StringValue')
                        """
                        subprocess.call(["icingacli", "director", "host", "delete", hostname])
                        response = client.delete_message(
                            QueueUrl=access['terminated_instances_queue'],
                            ReceiptHandle='XXXXXXXXXXXXXXXXxxxxxx'
                        )
                        """

    def is_json(self,  myjson):
        """Tests if the supplied string is valid json

        Args:
            myjson(string): string to be tested
        Returns:
            True: if provided string is json,
            False: otherwise
        Raises:
            ValueError: if string is not a valid json

        """
        try:
            json_object = json.loads(myjson)
        except ValueError, e:
            return False
        return True

multiaws = get_aws_instances("config.json")
multiaws.update_aws_hosts()
multiaws.remove_terminated_instances()