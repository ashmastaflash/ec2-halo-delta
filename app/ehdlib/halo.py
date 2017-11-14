import cloudpassage
import os
import re


class Halo(object):
    """Initialize with a dict containing Halo API key and secret."""
    def __init__(self, config):
        self.ua_string = self.get_ua_string
        if "api_host" in config:
            self.session = cloudpassage.HaloSession(config["api_key"],
                                                    config["api_secret"],
                                                    integration_string=self.ua_string,  # NOQA
                                                    api_host=config["api_host"])  # NOQA
        else:
            self.session = cloudpassage.HaloSession(config["api_key"],
                                                    config["api_secret"],
                                                    integration_string=self.ua_string)  # NOQA
        return

    def get_all_servers(self):
        """Get all servers from Halo API."""
        server_obj = cloudpassage.Server(self.session)
        result = server_obj.list_all()
        return result

    @classmethod
    def get_ua_string(cls):
        """Create the User-Agent string."""
        product = "ec2-halo-delta"
        version = cls.get_product_version()
        ua_string = product + "/" + version
        return ua_string

    @classmethod
    def get_product_version(cls):
        """Gets the version of the tool from the ``__init__.py`` file."""
        init = open(os.path.join(os.path.dirname(__file__),
                    "__init__.py")).read()
        rx_compiled = re.compile(r"\s*__version__\s*=\s*\"(\S+)\"")
        version = rx_compiled.search(init).group(1)
        return version
