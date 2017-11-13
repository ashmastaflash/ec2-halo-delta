from slackclient import SlackClient


class Slack(object):
    """This class handles all interaction with Slack.

    Attributes:
        token (str): Slack API token
        client (slackclient.SlackClient): Slack client object

    """

    def __init__(self, config):
        """Instantiation only creates the client attribute"""
        self.token = config["api_token"]
        self.botname = "Halo Footprinter"
        self.bot_avatar = "http://www.cloudpassage.com/wp-content/uploads/2016/12/don-operator.png"  # NOQA
        self.client = SlackClient(self.token)
        self.channel = config["default_channel_name"]
        if "routing_rules" in config:
            self.routing_rules = config["routing_rules"]
        else:
            self.routing_rules = {}
        if config["api_token"] is not None:
            self.is_active = True
        else:
            self.is_active = False

    def send_message(self, channel, message):
        """Send a message to a channel."""
        self.client.api_call("files.upload",
                             initial_comment="Halo Report",
                             channels=channel,
                             content=message,
                             filetype="text",
                             username=self.botname,
                             icon_url=self.bot_avatar)
        return

    def get_channel_id_reference(self):
        """Return a dictionary with key = channel name, value = id."""
        all_channels = self.client.api_call("channels.list")
        all_groups = self.client.api_call("groups.list")
        chan_groups = list(all_channels["channels"])
        chan_groups.extend(all_groups["groups"])
        retval = {c["name"]: c["id"] for c in chan_groups}
        return retval
