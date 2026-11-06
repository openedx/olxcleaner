# -*- coding: utf-8 -*-
"""
errorstore.py

Structures to accumulate and track errors in a course
"""
from collections import Counter

class ErrorStore(object):
    """Class to store all errors in an import"""

    def __init__(self, ignorelist=None):
        self.errors = []
        self.ignorelist = ignorelist if ignorelist else []

    def add_error(self, error):
        """Add an error to the list (but only if not ignored)"""
        if error.name not in self.ignorelist:
            self.errors.append(error)

    def return_error(self, error_level):
        """Returns True if the highest level error is at least error_level"""
        max_level = -1
        if self.errors:
            max_level = max([error.level_val for error in self.errors])
        return max_level >= error_level

    def summary(self):
        """
        Returns a dictionary keyed by error levels containing a counter
        of errors at that level keyed by error names
        """
        # Get a count of each level of error
        levelcounter = Counter([error.level for error in self.errors])
        # For each level, get a count of each type of error
        errors = {}
        for level in levelcounter:
            errors[level] = Counter([error.name for error in self.errors if error.level == level])
        return errors
