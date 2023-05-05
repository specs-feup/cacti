class InvalidTranspiler(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class IdempotencyException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class CorrectnessException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
