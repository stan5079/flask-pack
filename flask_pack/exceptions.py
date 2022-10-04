class FlaskPackException(Exception):
    """Base exception class."""
    pass


class StaticNotInitialized(FlaskPackException):
    """Raised when you perform a function but the package has not been initialized."""
    pass


class FileTypeUnsupported(FlaskPackException):
    """Raised when the filetype is unsupported."""
    pass


class FileNotFound(FlaskPackException):
    """Raised when a file could not be found."""
    pass
