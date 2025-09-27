

class LicenseExpiredError(Exception):
    """Raised when the license has expired"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
