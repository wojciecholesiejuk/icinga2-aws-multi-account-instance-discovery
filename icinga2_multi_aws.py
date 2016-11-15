import boto3
import pprint
import json
import os.path

class get_aws_instances:
    """ Retrieves EC2 instances from aws accounts and adds to/creates incinga config file for the 
    
    Step by step:
        - check for/read config file
        - connect to aws get instances based on defined accounts, regions and tags
        - write instaces to 'next' config files
        - compare with 'existing' config files, finish if no changes are detected
        - if changes detected:
            - backup old files
            - crate/delete/replace config files
            - restart service

    """
    restart_required = False
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
        self.create_next_hostfiles(self.list_instances())
        if self.compare_hostsfiles == True:
            self.remove_next_hostfiles()
            return True
        else:
            self.update_hostsfiles()
            self.restart_service()

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
        ### 
        pprint.pprint(instances)
        return instancesx

    def create_next_hostfiles(self, instances):
        pass

    def write_hostsfile(self, name, text):
        pass

    def read_hostsfile(self, file):
        pass

    def check_hostsfile_is_safe(self, file):
        pass

    def restart_service(self):
        pass

    def compare_hostsfiles(self, file1, file2):
        pass

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
