from utility import Utility


class Report(object):
    """We use this class to generate markdown reports."""
    @classmethod
    def create_stdout_report(cls, instances):
        """Expect a dictionary object. Produce a report, yo."""
        pieces = [cls.format_aws_instance(rep) for rep in sorted(instances.items())]  # NOQA
        result = "\n----------\n".join(pieces)
        return result

    @classmethod
    def create_slack_reports(cls, channel_reference, default_channel,
                             routing_rules, instances):
        """Expect a dictionary object. Produce reports.

        Returns:
            dict where {"channel": "report"}.

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
        instance_id = "Instance ID: {instance}".format(instance=aws_instance[0])  # NOQA
        aws_account = "AWS Account: {account}".format(account=aws_instance[1]["aws_account"])  # NOQA
        aws_region = "AWS Region: {region}".format(region=aws_instance[1]["aws_region"])  # NOQA
        key_name = "Key Name: {key_}".format(key_=aws_instance[1]["key_name"])
        launch = "Launched at: {launch}".format(launch=aws_instance[1]["launch_time"])  # NOQA
        vpc_id = "VPC ID: {vpc}".format(vpc=aws_instance[1]["vpc_id"])
        ordered_fields = [aws_account, aws_region, key_name, vpc_id,
                          instance_id, launch]
        return "\n".join(ordered_fields)
