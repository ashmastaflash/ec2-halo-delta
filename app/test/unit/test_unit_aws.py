import datetime
import imp
import os
import sys


here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, "../../")
module_name = "ehdlib"
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
ehdlib = imp.load_module(module_name, fp, pathname, description)


class TestUnitReport():
    def test_instance_metadata_cleanse(self):
        cleanse = ehdlib.AWS.instance_metadate_cleanse
        # All metadata
        metadata_1 = {"VpcId": "abc123",
                      "KeyName": "ssh_key.pem",
                      "LaunchTime": datetime.datetime.now()}
        # Missing VpcId
        metadata_2 = {"KeyName": "ssh_key.pem",
                      "LaunchTime": datetime.datetime.now()}
        # Missing KeyName
        metadata_3 = {"VpcId": "abc123",
                      "LaunchTime": datetime.datetime.now()}
        # Missing KeyName and VpcId:
        metadata_4 = {"LaunchTime": datetime.datetime.now()}
        for metadata in [metadata_1, metadata_2, metadata_3, metadata_4]:
            cleaned = cleanse(metadata, "account123", "nowhere-west-1")
            assert cleaned
            assert len(cleaned) == 5
        cleaned_2 = cleanse(metadata_4, "account456", "everywhere-east-2")
        assert cleaned_2["vpc_id"] == "NO VPC ID"
        assert cleaned_2["key_name"] == "NO KEY USED IN PROVISIONING"
