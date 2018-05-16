import boto3


class AWS(object):
    """Wraps all AWS interaction.  Pass in a dict containing configuration.

    Dict requires the following keys: ``api_key``, ``api_secret``.

    Optionally, the dict may have keys for ``accounts``, and ``role_name``.
    The value for ``accounts`` should be a list of strings where each string
    is an AWS account number. Each account number referenced in ``accounts``
    must contain a role with name matching ``role_name``. Each account in
    ``accounts`` is used with ``role_name`` to build an ARN for the role
    this tool will assume to inventory each account it has access to, via the
    ``api_key`` and ``api_secret``.
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
        """Return an ARN string.

        Args:
            account_no(str): AWS account number
            role_name(str): Name of the role to be identified by ARN.

        Returns:
            str: ARN for ``role_name`` in ``account_no``
        """
        arn = "arn:aws:iam::{account_no}:role/{role_name}".format(account_no=account_no, role_name=role_name)  # NOQA
        return arn

    def describe_all_ec2_instances(self):
        """Get an inventory of all AWS EC2 instances for accessible accounts.

        Returns:
            dict: Inventory of AWS EC2 instances.
        """
        inventory = {}
        for account in self.accounts:
            inventory.update(self.get_ec2_inventory_for_account(account))
        inventory.update(self.get_ec2_inventory_for_api_keys_default())
        return inventory

    def get_ec2_inventory_for_account(self, account_no):
        """Get EC2 inventory for numbered AWS account.

        Args:
            account_no(str): AWS account number

        Returns:
            dict: Inventory of AWS EC2 instances for ``account_no``.

        """
        retval = {}
        arn = self.build_arn(account_no, self.role_name)
        for region in self.ec2_regions:
            retval.update(self.get_all_for_region(region, arn))
        return retval

    def get_ec2_inventory_for_api_keys_default(self):
        """Get EC2 inventory for default account for key and secret.

        This instance method uses the AWS API key and secret the object was
        instantiated with to get an inventory of all instances across all
        regions.

        Returns:
            dict: Inventory of AWS EC2 instances.
        """
        retval = {}
        for region in self.ec2_regions:
            retval.update(self.get_all_for_region(region))
        return retval

    def get_all_for_region(self, region_name, arn=None):
        """Get all instances for a region.

        Handles pagination in the event there are more than 1000 instances
        in a region.

        Args:
            region_name(str): Name of AWS region to inventory.
            arn(str): Role ARN for enumerating instances across accounts.
                Defaults to ``None``, which will use the default account
                associated with the API keys this object was instantiated
                with.

        Return:
            dict: Inventory of AWS EC2 instances.
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
            session_token = creds["Credentials"]["SessionToken"]
            client = boto3.client('ec2', aws_access_key_id=temp_key,
                                  aws_secret_access_key=temp_secret,
                                  aws_session_token=session_token,
                                  region_name=region_name)
            # print("Getting inventory for %s, creds: %s" % (arn, creds))
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
        """Clean and sanitize instance metadata for use.

        If the EC2 instance was created without an SSH key, the ``key_name``
        in the output of this classmethod will be represented like this:
        ``NO KEY USED IN PROVISIONING``.

        Args:
            metadata(dict): Instance metadata returned from AWS SDK.
            aws_account(str): Account number for AWS instance.
            aws_region(str): Region containing the AWS instance.

        Returns:
            dict: Simple structure describing AWS EC2 instance.

        """
        for meta_key in [("KeyName", "NO KEY USED IN PROVISIONING"),
                         ("VpcId", "NO VPC ID")]:
            if meta_key[0] not in metadata:
                metadata[meta_key[0]] = meta_key[1]
        retval = {"vpc_id": metadata["VpcId"],
                  "aws_account": aws_account,
                  "key_name": metadata["KeyName"],
                  "aws_region": aws_region,
                  "launch_time": metadata["LaunchTime"].isoformat()}
        return retval
