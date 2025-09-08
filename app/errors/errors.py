

class KaleemException(Exception):
    """
    Custom exception class for Kaleem application.
    """
    def __init__(self, name: str, status_code: int = 400):
        self.name = name
        self.status_code = status_code