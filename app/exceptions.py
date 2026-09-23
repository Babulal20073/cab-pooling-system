class AppException(Exception):
    pass


class EmailAlreadyExistsError(AppException):
    pass


class InvalidCredentialsError(AppException):
    pass