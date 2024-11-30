


class HttpError(Exception):
    """Represents an HTTP error with reason and status code."""
    def __init__(self, reason: str, status: int, tip: str = None):
        super().__init__(reason)
        self.reason = reason
        self.status = status
        self.tip = tip

    def __str__(self) -> str:
        return f'\n\nHttpError({self.status} {self.reason})\nTip: {self.tip}\n'