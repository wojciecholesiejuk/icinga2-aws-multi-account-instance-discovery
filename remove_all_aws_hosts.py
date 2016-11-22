from icinga2_multi_aws import get_aws_instances

multiaws = get_aws_instances("/srv/icinga2-aws-multi-account-instance-discovery/config.json")
multiaws.remove_all_aws_hosts()