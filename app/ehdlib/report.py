class Report(object):
    """We use this class to generate markdown reports."""
    @classmethod
    def create_report(cls, instances):
        """Expect a dictionary object. Produce a report, yo."""
        pieces = [cls.format_aws_instance(rep) for rep in sorted(instances.items())]  # NOQA
        result = "\n----------\n".join(pieces)
        return result

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
