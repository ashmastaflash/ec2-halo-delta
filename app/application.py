#!/usr/bin/env python
from ehdlib import AWS, Halo, Report, Slack, Utility


def main():
    # Get application configuration
    aws_config = Utility.get_aws_config()
    halo_config = Utility.get_halo_config()
    slack_config = Utility.get_slack_config()

    # Set up Slack object
    slack = Slack(slack_config)

    # Get a list of all Halo agents with EC2 metadata
    halo_obj = Halo(halo_config)
    halo_servers = halo_obj.get_all_servers()

    # Get a dict of all AWS instances for all accounts
    aws_obj = AWS(aws_config)
    instances = aws_obj.describe_all_ec2_instances()

    # Remove the Halo-protected instances from the AWS instances dict.
    for server in halo_servers:
        try:
            instance_id = server["aws_ec2"]["ec2_instance_id"]
        except KeyError:
            continue
        if instance_id in instances:
            del(instances[instance_id])

    # A report is sent to stdout
    report = Report.create_report(instances)
    print report

    # A consolidated report is produced and dropped into the main channel

    # If routing rules exist, send individual channel reports as appropriate
    return


if __name__ == "__main__":
    main()
