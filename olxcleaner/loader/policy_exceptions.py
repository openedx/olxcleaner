# -*- coding: utf-8 -*-
"""
policy_exceptions.py

Contains exception definitions for policy file loading
"""
from olxcleaner.exceptions import CourseError, ErrorLevel

class NoRunName(CourseError):
    """The course tag has no `url_name`, and hence no run name. This is a required parameter for a course."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The course tag has no url_name."

class PolicyNotFound(CourseError):
    """A policy file was not found."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The policy file '{filename}' was not found."

class BadPolicy(CourseError):
    """A policy file was not valid JSON."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The policy file '{filename}' has invalid JSON: {kwargs['msg']}"
