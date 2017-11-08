from slackclient import SlackClient


class Slack(object):
    """This class handles all interaction with Slack.

    Attributes:
        token (str): Slack API token
        client (slackclient.SlackClient): Slack client object

    """

    def __init__(self, config):
        """Instantiation only creates the client attribute"""
        self.token = config["slack_api_token"]
        self.botname = "Halo Footprinter"
        self.bot_avatar = "http://www.cloudpassage.com/wp-content/uploads/2016/12/don-operator.png"  # NOQA
        self.client = SlackClient(self.token)
        self.channel = config["default_channel_name"]

    def send_message(self, message, channel):
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
        """INCOMPLETE!  Return a dictionary with channel name key, value id."""
        all_channels = self.client.api_call("channels.list")
        all_groups = self.client.api_call("groups.list")
        chan_groups = list(all_channels["channels"])
        chan_groups.extend(all_groups["groups"])
        return chan_groups
