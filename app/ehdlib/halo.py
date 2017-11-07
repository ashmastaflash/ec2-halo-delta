import cloudpassage


class Halo(object):
    """Initialize with a dict containing Halo API key and secret."""
    def __init__(self, config):
        if "api_host" in config:
            self.session = cloudpassage.HaloSession(config["api_key"],
                                                    config["api_secret"],
                                                    api_host=config["api_host"])  # NOQA
        else:
            self.session = cloudpassage.HaloSession(config["api_key"],
                                                    config["api_secret"])
        return

    def get_all_servers(self):
        server_obj = cloudpassage.Server(self.session)
        result = server_obj.list_all()
        return result
