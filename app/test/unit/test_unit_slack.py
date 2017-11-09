import imp
import os
import sys


here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, "../../")
module_name = "ehdlib"
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
ehdlib = imp.load_module(module_name, fp, pathname, description)


class TestUnitSlack():
    def get_slack_config_slim_zero(self, monkeypatch):
        config = ehdlib.Utility.get_slack_config()
        return ehdlib.Slack(config)

    def get_slack_config_slim_1(self, monkeypatch):
        monkeypatch.setenv("SLACK_API_TOKEN", "HOWDY")
        config = ehdlib.Utility.get_slack_config()
        return ehdlib.Slack(config)

    def get_slack_config_full(self, monkeypatch):
        input_str = "vpc_id,123,channel1;vpc_id,456,channel2;key_name,abc,channel3"  # NOQA
        monkeypatch.setenv("SLACK_API_TOKEN", "HOWDY")
        monkeypatch.setenv("SLACK_CHANNEL", "HIDY")
        monkeypatch.setenv("SLACK_ROUTING", input_str)
        config = ehdlib.Utility.get_slack_config()
        return ehdlib.Slack(config)

    def test_does_slack_module_deactivate(self, monkeypatch):
        slack = self.get_slack_config_slim_zero(monkeypatch)
        assert slack.is_active is False

    def test_does_slack_module_have_empy_dict_for_routes(self, monkeypatch):
        slack = self.get_slack_config_slim_1(monkeypatch)
        assert slack.routing_rules == {}

    def test_does_slack_module_have_dict_for_routes(self, monkeypatch):
        slack = self.get_slack_config_full(monkeypatch)
        assert slack.routing_rules != {}
