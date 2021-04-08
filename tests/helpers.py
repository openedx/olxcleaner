"""
helpers.py

Helper routines for testing with ErrorStore objects
"""

def assert_error(errorstore, errorclass, file, msg):
    """Search through the errorstore to assert that the given error was captured, and remove it"""
    for idx, error in enumerate(errorstore.errors):
        if isinstance(error, errorclass) and error.filename == file and error.description == msg:
            del errorstore.errors[idx]
            return
    raise ValueError("Error not found")

def assert_not_error(errorstore, errorclass, file, msg):
    """Search through the errorstore to assert that the given error is not present"""
    for idx, error in enumerate(errorstore.errors):
        if isinstance(error, errorclass) and error.filename == file and error.description == msg:
            raise ValueError("Error found")
    return

def assert_caught_all_errors(errorstore):
    """Demand that all errors in the errorstore were accounted for through assert_error"""
    if errorstore.errors:
        for error in errorstore.errors:
            print(error, error.description)
        raise ValueError("Found leftover errors")
