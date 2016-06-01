class RequestError(Exception):
    def __init__(self, response):
        self.response = response


class NotAuthenticatedError(RequestError):
    """Failed to connect to the Beam server."""
    pass


class UnknownError(RequestError):
    pass
