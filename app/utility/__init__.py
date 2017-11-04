class Utility(object):
    """This class contains functionality that make use of data from multiple
    external services.
    """
    @classmethod
    def get_channel_for_message(cls, channel_reference, instance_metadata,
                                routing_rules, default_channel_name):
        """Return channel ID for messages pertaining to instance.

        Args:
            channel_reference(dict): Channel name is key, value is channel ID.
            instance_metadata(dict):
            routing_rules(dict): Rules for routing messages.  Formatted like
                this: {"ROUTING_KEY": {"ROUTING_KEY_VALUE": "CHANNEL_NAME",
                                       "ROUTING_KEY_VALUE": "CHANNEL_NAME"}}
            default_channel_name(str): Name of default channel for alerts
        """

        priorities = ["key_name", "vpc_id", "aws_region", "aws_account"]
        target_channel = channel_reference[default_channel_name]
        for priority in priorities:
            try:
                target_channel = channel_reference[routing_rules[priority][instance_metadata[priority]]]  # NOQA
                break
            except KeyError:
                pass
        return target_channel
