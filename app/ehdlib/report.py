import base64
import csv
import io
from utility import Utility


class Report(object):
    """We use this class to generate text reports."""
    @classmethod
    def create_csv_report(cls, instances):
        """Expect a dictionary object, produce text in CSV format."""
        rows = [cls.format_aws_instance_csv(rep) for rep in sorted(instances.items())]  # NOQA
        fieldnames = ["instance_id", "aws_account", "aws_region", "key_name",
                      "launch_time", "vpc_id"]
        ephemeral_obj = io.BytesIO()
        csv_writer = csv.DictWriter(ephemeral_obj, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(rows)
        result = base64.b64encode(ephemeral_obj.getvalue())
        ephemeral_obj.close()
        return result

    @classmethod
    def create_stdout_report(cls, instances):
        """Expect a dictionary object, produce text appropriate for stdout."""
        pieces = [cls.format_aws_instance(rep) for rep in sorted(instances.items())]  # NOQA
        result = "\n----------\n".join(pieces)
        return result

    @classmethod
    def create_slack_reports(cls, channel_reference, default_channel,
                             routing_rules, instances):
        """Create a plaintext report for Slack.

        Args:
            channel_reference(dict): Keys are channel names, values are channel
                IDs.
            default_channel(str): Name of default Slack channel.
            routing_rules(dict): Rules for routing messages to different Slack
                channels.  Formatted like
                {"metadata_field_name":
                    {"metadata_field_value_to_match": "slack_channel_name"}}
            instances(dict): Instance metadata.

        Returns:
            dict: {"channel": "report"} where "channel" is the Slack channel
                ID and "report" is the text of the report.
        """
        organized = {}
        # Group by target Slack channel.
        for instance in instances:
            channel = Utility.get_channel_for_message(channel_reference,
                                                      instance, routing_rules,
                                                      default_channel)
            if channel not in organized:
                organized[channel] = []
            organized[channel].append(instance)
        # Build report per channel, each sorted by instance ID.
        report = {}
        for target, content in organized.items():
            x_content = {c.keys()[0]: c.values()[0] for c in content}
            report[target] = cls.create_stdout_report(x_content)
        return report

    @classmethod
    def format_aws_instance(cls, aws_instance):
        """Format an AWS instance's metadata for reporting.

        Args:
            aws_instance(tuple): Formatted like this:
                ("i-231423452", {"aws_account": "12345",
                                 "aws_region": "us-east-1",
                                 "key_name": "my_ssh_key",
                                 "launch_time": "1999-12-31T23:59.9"}}

        """
        instance_id = "Instance ID: {instance}".format(instance=aws_instance[0])  # NOQA
        aws_account = "AWS Account: {account}".format(account=aws_instance[1]["aws_account"])  # NOQA
        aws_region = "AWS Region: {region}".format(region=aws_instance[1]["aws_region"])  # NOQA
        key_name = "Key Name: {key_}".format(key_=aws_instance[1]["key_name"])
        launch = "Launched at: {launch}".format(launch=aws_instance[1]["launch_time"])  # NOQA
        vpc_id = "VPC ID: {vpc}".format(vpc=aws_instance[1]["vpc_id"])
        ordered_fields = [aws_account, aws_region, key_name, vpc_id,
                          instance_id, launch]
        return "\n".join(ordered_fields)

    @classmethod
    def format_aws_instance_csv(cls, aws_instance):
        """Format an AWS instance's metadata for reporting in CSV format.

        Args:
            aws_instance(tuple): Formatted like this:
                ("i-231423452", {"aws_account": "12345",
                                 "aws_region": "us-east-1",
                                 "key_name": "my_ssh_key",
                                 "launch_time": "1999-12-31T23:59.9"}}
        Returns:
            dict: {"instance_id": "i-12345"
                   "aws_account": "12345",
                   "aws_region": "us-east-1",
                   "key_name": "my_ssh_key",
                   "launch_time": "1999-12-31T23:59.9"}

        """
        result = {"instance_id": aws_instance[0],
                  "aws_account": aws_instance[1]["aws_account"],
                  "aws_region": aws_instance[1]["aws_region"],
                  "key_name": aws_instance[1]["key_name"],
                  "launch_time": aws_instance[1]["launch_time"],
                  "vpc_id": aws_instance[1]["vpc_id"]}
        return result
