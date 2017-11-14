#!/usr/bin/env python
import os
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
    if os.getenv("OUTPUT_FORMAT", "plaintext") == "csv":
        report = Report.create_csv_report(instances)
    else:
        report = Report.create_stdout_report(instances)
    print report

    # Build segmented Slack report, if Slack is active
    if slack.is_active is True:
        channel_reference = slack.get_channel_id_reference()
        reports = report.create_slack_reports(channel_reference,
                                              slack_config["default_channel_name"],  # NOQA
                                              slack_config["routing_rules"],
                                              instances)
        for channel, message in reports.items():
            slack.send_message(channel, message)
    return


if __name__ == "__main__":
    main()
