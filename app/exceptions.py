#auth related errors
class AppException(Exception):
    pass


class EmailAlreadyExistsError(AppException):
    pass

#admin related errors
class InvalidCredentialsError(AppException):
    pass
class OfficeAlreadyExistsError(AppException):
    pass

class OfficeNotFoundError(AppException):
    pass

#booking related errors
class ShiftNotFoundError(AppException):
    pass


class DuplicateBookingError(AppException):
    pass


class BookingNotFoundError(AppException):
    pass