# EC2-Halo Footprint Delta Reporter

[![Build Status](https://travis-ci.org/cloudpassage/ec2-halo-delta.svg?branch=master)](https://travis-ci.org/cloudpassage/ec2-halo-delta)

Report on all EC2 instances which do not have a Halo agent installed.

## Requirements

* Account access:
    * CloudPassage Halo read-only API keys (root group)
    * AWS API keys, need to be able to fetch EC2 instance metadata
    * Slack API keys
* Infrastructure:
    * Docker engine

## Running

First, set these mandatory environment variables:

| Variable name            | Purpose                                     |
|--------------------------|---------------------------------------------|
| `AWS_ACCESS_KEY_ID`      | AWS API key with EC2 read-only access       |
| `AWS_SECRET_ACCESS_KEY`  | Secret corresponding to `AWS_ACCESS_KEY_ID` |
| `HALO_API_KEY`           | CloudPassage Halo API key ID                |
| `HALO_API_SECRET_KEY`    | Secret corresponding to `HALO_API_KEY`      |

Optionally, set these environment variables, if your environment requires them:

| Variable name            | Purpose                                                                |
|--------------------------|------------------------------------------------------------------------|
| `HALO_API_HOSTNAME`      | Hostname for Halo API.  Default: `api.cloudpassage.com`                |
| `SLACK_ROUTING`          | Slack message routing rules.  See below...                             |
| `SLACK_CHANNEL`          | Default channel for Slack notifications. If unset, defaults to `halo`. |
| `SLACK_API_TOKEN`        | API token for Slack                                                    |
| `AWS_ACCOUNT_NUMBERS`    | Account numbers for accounts to enumerate. See below...                |
| `AWS_ROLE_NAME`          | Role name for enumerating EC2 instances across accounts.  See below... |
| `OUTPUT_FORMAT`          | Define alternate output format.  Currently supported: `csv`            |


### SLACK_ROUTING setting

The optional environment variable, `SLACK_ROUTING`, below, allows you to route
Slack notifications to specific channels, based on EC2 instance metadata.  The
metadata items you can use for routing are AWS account number, VPC ID, AWS
region, and key name, and are described in deeper detail below:

| Priority | Routing key   | Description                                        |
|----------|---------------|----------------------------------------------------|
|        1 | `key_name`    | Name of SSH key used when provisioning instance    |
|        2 | `vpc_id`      | ID of VPC containing EC2 instance                  |
|        3 | `aws_region`  | Region in which the EC2 instance is operating      |
|        4 | `aws_account` | Account number for account containing EC2 instance |

Each instance detected without Halo will be compared against the list of
`SLACK_ROUTING` matches.  Routing keys will be compared in order of priority,
from 1-4. Once a match is made, the message will be sent. Sending the same
notification to multiple channels is not currently possible.

The `SLACK_ROUTING` environment variable is constructed in this format:
`ROUTING_KEY,ROUTING_KEY_VALUE,CHANNEL;ROUTING_KEY,ROUTING_KEY_VALUE,CHANNEL`.
Routing instructions are separated by a semicolon `;`, and the routing key,
routing key value, and Slack channel are separated by a comma.  No spaces.

An example scenario, to help explain how routing works:

You are in charge of three AWS accounts (account numbers `123`, `456`, and
`789`, for the sake of simplicity), and depending on the workload's
account, different teams will be responsible for installing the Halo agent.  
Account `123` belongs to the production engineering group. Account `456`
(dev/test) and `789` (user acceptance) belong to pre-production engineering.
Production engineering's slack channel is `#prod-eng` and pre-production
engineering's Slack channel is `#pre-prod-eng`.  This is what the rules look
like, from a logical standpoint:

```
| Routing key   | Routing key value | Slack channel  |
|---------------|-------------------|----------------|
| `AWS_ACCOUNT` | `123`             | `prod-eng`     |
| `AWS_ACCOUNT` | `456`             | `pre-prod-eng` |
| `AWS_ACCOUNT` | `789`             | `pre-prod-eng` |

```

That translates into the `SLACK_ROUTING` environment variable like this:

```
SLACK_ROUTING="AWS_ACCOUNT,123,prod-eng;AWS_ACCOUNT,456,pre-prod-eng;AWS_ACCOUNT,789,pre-prod-eng"
```

### AWS_ROLE_NAME setting

The `AWS_ROLE_NAME` setting defines the name of a role which exists in all
monitored AWS accounts.  This role must have the `AmazonEC2ReadOnlyAccess`
IAM policy attached.  This role name must exist in all monitored accounts,
and a trust relationship with the user account represented by
`AWS_ACCESS_KEY_ID` must exist, so that this tool may use `AWS_ACCESS_KEY_ID`
to assume the role in the monitored account that allows collection of EC2
metadata.  This variable is used in constructing each of the ARNs used for
collecting EC2 metadata.  For instance, if the `AWS_ROLE_NAME` is
`ec2-instanceinfo` and one of the account numbers in `AWS_ACCOUNT_NUMBERS` is
`12345`, the ARN of the role assumed by this tool to collect EC2 instance
information is `arn:aws:iam::12345:role/ec2-instanceinfo`

### AWS_ACCOUNT_NUMBERS setting

The `AWS_ACCOUNT_NUMBERS` setting is a list of account numbers, separated by
a semicolon `;`, which represent accounts in which a role indicated by
`AWS_ROLE_NAME` exists with an `AmazonEC2ReadOnlyAccess` policy attached.
If this tool is expected to monitor three AWS accounts, with account numbers
`12345`, `67890`, and `76543`, the correct wetting for this environment
variable would look like this:

```
AWS_ACCOUNT_NUMBERS="12345;67890;76543"
```

Assuming the above settings exist for `AWS_ROLE_NAME` and `AWS_ACCOUNT_NUMBERS`,
the resulting ARNs used to access EC2 instance information will be:

```
arn:aws:iam::12345:role/ec2-instanceinfo
arn:aws:iam::67890:role/ec2-instanceinfo
arn:aws:iam::76543:role/ec2-instanceinfo
```

### Running the Tool

* First, build the container:

```
docker build -t footprinter -f ./Dockerfile .
```

* Human-readable output, only required environment variables:

```
docker run -it --rm \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e HALO_API_KEY=$HALO_API_KEY \
    -e HALO_API_SECRET_KEY=$HALO_API_SECRET_KEY \
    footprinter
```

* CSV output, scanning multiple accounts, and saved to a file.  CSV output is base64-encoded. Notice that `AWS_ROLE_NAME` and `AWS_ACCOUNT_NUMBERS` are both set):

```
docker run -it --rm \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e HALO_API_KEY=$HALO_API_KEY \
    -e HALO_API_SECRET_KEY=$HALO_API_SECRET_KEY \
    -e AWS_ROLE_NAME=$AWS_ROLE_NAME \
    -e AWS_ACCOUNT_NUMBERS=$AWS_ACCOUNT_NUMBERS \
    -e OUTPUT_FORMAT=csv \
    footprinter | base64 --decode > ./aws_halo_footprint_delta.csv
```

## Implementation Notes

If you use non-root, non-administrative API keys for cross-account access,
you will need to set up the IAM account (the one attached to the API keys you
use for this tool) to use STS to assume the role in the other monitored
accounts.  

In this example scenario, we call the account containing the IAM user (in this
example, called `halo-footprinter`) that will access other accounts for the
purpose of gathering an inventory of EC2 instances, the `Administrative` account.  
The account that contains a role named `ec2-instance-info` that the
`Administrative` account will assume for the purposes of inventory collection,
is called `Monitored`.  The `Administrative` account has AWS account number
`98765`.  The `Monitored` account has AWS account number `12345`

This is an example policy which should be attached to the API keys in the
`Administrative` account:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1510597306000",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole"
            ],
            "Resource": [
                "arn:aws:iam::12345:role/ec2-instance-info"
            ]
        }
    ]
}

```

This policy needs to be attached to the role named `ec2-instance-info` in
AWS account `12345` (the `Monitored` account) where `halo-footprinter` is
the name of the account with the API keys you're using and replacing
`98765` with the account number of the `Administrative` AWS account:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::98765:user/halo-footprinter"
      },
      "Action": "sts:AssumeRole",
      "Condition": {}
    }
  ]
}

<!---
#CPTAGS:community-supported audit
#TBICON:images/python_icon.png
-->
