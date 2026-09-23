class AppException(Exception):
    pass


class EmailAlreadyExistsError(AppException):
    pass


class InvalidCredentialsError(AppException):
    pass


class OfficeAlreadyExistsError(AppException):
    pass


class OfficeNotFoundError(AppException):
    pass


class ShiftNotFoundError(AppException):
    pass


class DuplicateBookingError(AppException):
    pass


class BookingNotFoundError(AppException):
    pass


class NoValidRouteError(AppException):
    pass