import imp
import os
import sys


here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, "../../")
module_name = "ehdlib"
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
ehdlib = imp.load_module(module_name, fp, pathname, description)


class TestUnitUtility():
    def test_get_channel_for_message(self):
        util = ehdlib.Utility
        default_channel_name = "halo"
        channel_reference = {"somechannel": "one",
                             "dontpickme": "two",
                             "halo": "whateverchannel"}
        instance_metadata_1 = {"instance_1": {"vpc_id": "abc123",
                                              "aws_account": "098978rtyu",
                                              "aws_region": "sxsw",
                                              "key_name": "llaves",
                                              "instance_id": "098978rtyu"}}
        instance_metadata_2 = {"instance_2": {"vpc_id": "abc1234",
                                              "aws_account": "098978rtyu",
                                              "aws_region": "sxsw",
                                              "key_name": "llaves",
                                              "instance_id": "098978rtyu"}}
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

    def test_get_aws_config_slim_1(self, monkeypatch):
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "HOWDY")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "HIDY")
        aws_config = ehdlib.Utility.get_aws_config()
        assert aws_config["api_key"] == "HOWDY"
        assert aws_config["api_secret"] == "HIDY"
        assert "accounts" not in aws_config

    def test_get_aws_config_slim_2(self, monkeypatch):
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "HOWDY")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "HIDY")
        monkeypatch.setenv("AWS_ACCOUNT_NUMBERS", "12345;67890")
        aws_config = ehdlib.Utility.get_aws_config()
        assert aws_config["api_key"] == "HOWDY"
        assert aws_config["api_secret"] == "HIDY"
        assert "accounts" not in aws_config

    def test_get_aws_config_slim_3(self, monkeypatch):
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "HOWDY")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "HIDY")
        monkeypatch.setenv("AWS_ROLE_NAME", "HIDYHIDYHIDYHI")
        aws_config = ehdlib.Utility.get_aws_config()
        assert aws_config["api_key"] == "HOWDY"
        assert aws_config["api_secret"] == "HIDY"
        assert "accounts" not in aws_config
        assert "role_name" not in aws_config

    def test_get_aws_config_full(self, monkeypatch):
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "HOWDY")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "HIDY")
        monkeypatch.setenv("AWS_ACCOUNT_NUMBERS", "12345;67890")
        monkeypatch.setenv("AWS_ROLE_NAME", "HIDYHIDYHIDYHI")
        aws_config = ehdlib.Utility.get_aws_config()
        assert aws_config["api_key"] == "HOWDY"
        assert aws_config["api_secret"] == "HIDY"
        assert "accounts" in aws_config
        assert "role_name" in aws_config
        assert len(aws_config["accounts"]) == 2

    def test_get_halo_config_slim(self, monkeypatch):
        monkeypatch.setenv("HALO_API_KEY", "HOWDY")
        monkeypatch.setenv("HALO_API_SECRET_KEY", "HIDY")
        halo_config = ehdlib.Utility.get_halo_config()
        assert "api_host" not in halo_config
        assert len(halo_config.items()) == 2

    def test_get_halo_config_full(self, monkeypatch):
        monkeypatch.setenv("HALO_API_KEY", "HOWDY")
        monkeypatch.setenv("HALO_API_SECRET_KEY", "HIDY")
        monkeypatch.setenv("HALO_API_HOST", "HODEHODEHODEHO")
        halo_config = ehdlib.Utility.get_halo_config()
        assert "api_host" in halo_config
        assert len(halo_config.items()) == 3

    def test_build_routing_rules(self, monkeypatch):
        input_str = "vpc_id,123,channel1;vpc_id,456,channel2;key_name,abc,channel3"  # NOQA
        expected = {"vpc_id": {"123": "channel1", "456": "channel2"},
                    "key_name": {"abc": "channel3"}}
        monkeypatch.setenv("SLACK_ROUTING", input_str)
        actual = ehdlib.Utility.build_routing_rules()
        assert expected == actual

    def test_get_slack_config_slim_1(self, monkeypatch):
        monkeypatch.setenv("SLACK_API_TOKEN", "HOWDY")
        result = ehdlib.Utility.get_slack_config()
        assert result["default_channel_name"] == "halo"
        assert result["api_token"] == "HOWDY"
        assert "routing_rules" not in result

    def test_get_slack_config_slim_2(self, monkeypatch):
        monkeypatch.setenv("SLACK_API_TOKEN", "HOWDY")
        monkeypatch.setenv("SLACK_CHANNEL", "HIDY")
        result = ehdlib.Utility.get_slack_config()
        assert result["default_channel_name"] == "HIDY"
        assert result["api_token"] == "HOWDY"
        assert "routing_rules" not in result

    def test_get_slack_config_full(self, monkeypatch):
        input_str = "vpc_id,123,channel1;vpc_id,456,channel2;key_name,abc,channel3"  # NOQA
        monkeypatch.setenv("SLACK_API_TOKEN", "HOWDY")
        monkeypatch.setenv("SLACK_CHANNEL", "HIDY")
        monkeypatch.setenv("SLACK_ROUTING", input_str)
        result = ehdlib.Utility.get_slack_config()
        assert result["default_channel_name"] == "HIDY"
        assert result["api_token"] == "HOWDY"
        assert "routing_rules" in result
