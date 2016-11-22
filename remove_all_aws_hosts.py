from multi_aws import process_icinga2_aws_instances

multiaws = process_icinga2_aws_instances("/srv/icinga2-aws-multi-account-instance-discovery/config.json")
multiaws.remove_all_aws_hosts()