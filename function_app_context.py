from logging import Logger


class Context:
    def __init__(self):
        self.session = None
        self.KEY : str = None
        self.logging : Logger = None
context = Context()