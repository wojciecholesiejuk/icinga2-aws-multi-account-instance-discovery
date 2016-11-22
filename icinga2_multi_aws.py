from multi_aws import process_icinga2_aws_instances

multiaws = process_icinga2_aws_instances("/srv/icinga2-aws-multi-account-instance-discovery/config.json")
multiaws.update_aws_hosts()
multiaws.remove_terminated_instances()