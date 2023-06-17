class ChannelNotDefined(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "More than one tenant exists. Specify which tenant to use."
        super().__init__(msg)


class NoDefaultChannel(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "A default tenant does not exist."
        super().__init__(msg)
