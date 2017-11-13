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
    def test_create_slack_reports(self):
        report = ehdlib.Report
        default_channel_name = "halo"
        channel_reference = {"somechannel": "one",
                             "dontpickme": "two",
                             "halo": "whateverchannel"}
        instance_metadata_1 = {"Instance_1": {"vpc_id": "abc123",
                                              "aws_account": "098978rtyu",
                                              "aws_region": "sxsw",
                                              "key_name": "llaves",
                                              "launch_time": "noonish"}}
        instance_metadata_2 = {"Instance_2": {"vpc_id": "987cde",
                                              "aws_account": "098978rtyua",
                                              "aws_region": "sxsw",
                                              "key_name": "llaves",
                                              "launch_time": "noonish"}}
        routing_rules = {"key_name": {"somesuch": "nochannelblah"},
                         "vpc_id": {"abc123": "somechannel",
                                    "987cde": "dontpickme"}}
        results = report.create_slack_reports(channel_reference,
                                              default_channel_name,
                                              routing_rules,
                                              [instance_metadata_1,
                                               instance_metadata_2])
        assert len(results.keys()) == 2
        for result in results:
            assert isinstance(result[0], str)
            assert isinstance(result[1], str)
