class BaseCustomReport(object):
    template = None

    def get_context(self, export):
        raise "Not implemented"

    def __init__(self, template) -> None:
        self.template = template
