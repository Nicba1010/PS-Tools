class InvalidISODateException(Exception):
    def __init__(self, reason: str):
        super(InvalidISODateException, self).__init__(f"ISO date doesn't match specified format, reason: {reason}")
