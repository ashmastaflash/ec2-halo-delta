import imp
import os
import sys


here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, "../../")
module_name = "utility"
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
utility = imp.load_module(module_name, fp, pathname, description)


class TestUnitUtility():
    def test_get_channel_for_message(self):
        util = utility.Utility
        default_channel_name = "halo"
        channel_reference = {"somechannel": "one",
                             "dontpickme": "two",
                             "halo": "whateverchannel"}
        instance_metadata_1 = {"vpc_id": "abc123",
                               "instance_id": "098978rtyu"}
        instance_metadata_2 = {"vpc_id": "abc1234",
                               "instance_id": "098978rtyu"}
        routing_rules = {"instance_id": {"somesuch": "nochannelblah"},
                         "vpc_id": {"abc123": "somechannel",
                                    "987cde": "dontpickme"}}
        expected_channel = "one"
        actual_channel_1 = util.get_channel_for_message(channel_reference,
                                                        instance_metadata_1,
                                                        routing_rules,
                                                        default_channel_name)
        actual_channel_2 = util.get_channel_for_message(channel_reference,
                                                        instance_metadata_2,
                                                        routing_rules,
                                                        default_channel_name)
        assert actual_channel_1 == expected_channel   # Test against vpc_id
        assert actual_channel_2 == "whateverchannel"  # Test against default
