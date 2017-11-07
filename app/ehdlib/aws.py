import boto3


class AWS(object):
    """Wraps all AWS interaction.  Pass in a dict containing configuration.

    Dict requires the following keys: ``api_key``, ``api_secret``.

    Optionally, the dict may have keys for ``accounts``, and ``role_name``.
    """
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.api_secret = config["api_secret"]
        ec2_client = boto3.client('ec2', aws_access_key_id=self.api_key,
                                  aws_secret_access_key=self.api_secret,
                                  region_name='us-east-1')
        regions_raw = ec2_client.describe_regions()["Regions"]
        self.ec2_regions = [region["RegionName"] for region in regions_raw]
        self.accounts = []
        self.role_name = None
        if "accounts" in config:
            self.accounts = config["accounts"]
        if "role_name" in config:
            self.role_name = config["role_name"]
        return

    @classmethod
    def build_arn(cls, account_no, role_name):
        arn = "arn:aws:iam::{account_no}:role/{role_name}".format(account_no=account_no, role_name=role_name)  # NOQA
        return arn

    def describe_all_ec2_instances(self):
        inventory = {}
        for account in self.accounts:
            inventory.update(self.get_ec2_inventory_for_account(account))
        inventory.update(self.get_ec2_inventory_for_api_keys_default())
        return inventory

    def get_ec2_inventory_for_account(self, account_no):
        retval = {}
        arn = self.build_arn(account_no, self.role_name)
        for region in self.ec2.regions:
            retval.update(self.get_all_for_region_account(region, arn))
        return retval

    def get_ec2_inventory_for_api_keys_default(self):
        """Does not specify role for account, gets instances for default
        account attached to API keys.
        """
        retval = {}
        for region in self.ec2_regions:
            retval.update(self.get_all_for_region(region))
        return retval

    def get_all_for_region(self, region_name, arn=None):
        """Handles pagination in the event there are more than 1000 instances
        in a region.
        """
        retval = {}
        more_pages = True
        next_token = ""
        if arn:
            sts_client = boto3.client('sts')
            creds = sts_client.assume_role(RoleArn=arn,
                                           RoleSessionName="HaloFootprinter")
            temp_key = creds["Credentials"]["AccessKeyId"]
            temp_secret = creds["Credentials"]["SecretAccessKey"]
            client = boto3.client('ec2', aws_access_key_id=temp_key,
                                  aws_secret_access_key=temp_secret,
                                  region_name=region_name)
        else:
            client = boto3.client('ec2', aws_access_key_id=self.api_key,
                                  aws_secret_access_key=self.api_secret,
                                  region_name=region_name)
        aws_account = ""
        while more_pages:
            if next_token == "":
                response = client.describe_instances()
            else:
                response = client.describe_instances(NextToken=next_token)
            if "NextToken" in response:
                next_token = response["NextToken"]
            else:
                next_token = ""
                more_pages = False
            for reservation in response["Reservations"]:
                aws_account = reservation["OwnerId"]
                for instance in reservation["Instances"]:
                    retval[instance["InstanceId"]] = self.instance_metadate_cleanse(instance,  # NOQA
                                                                                    aws_account,  # NOQA
                                                                                    region_name)  # NOQA
        return retval

    @classmethod
    def instance_metadate_cleanse(cls, metadata, aws_account, aws_region):
        retval = {"vpc_id": metadata["VpcId"],
                  "aws_account": aws_account,
                  "key_name": metadata["KeyName"],
                  "aws_region": aws_region,
                  "launch_time": metadata["LaunchTime"].isoformat()}
        return retval
