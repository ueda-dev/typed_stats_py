class ProtocolViolationException(Exception):
    pass

class InvalidTypeException(Exception):
    def __init__(self, expected_type, actual_type):
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.message = f"Expected type {expected_type}, but got {actual_type}"
        super().__init__(self.message)