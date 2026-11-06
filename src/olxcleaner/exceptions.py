# -*- coding: utf-8 -*-
"""
exceptions.py

Contains base classes and supporting structures for describing errors
"""
from abc import ABC, abstractmethod
from enum import Enum


class ErrorLevel(Enum):
    """Levels of errors"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class CourseError(ABC):
    """
    Abstract class describing an error.
    Subclasses should use their docstring to describe themselves and set their error level.
    They should use their __init__ method to construct the error description.
    """
    _level = ErrorLevel.DEBUG
    _filename = ""  # To be set in init
    _description = ""  # To be set in init

    def __repr__(self):  # pragma: no cover
        return f"<{self.__class__.__name__} error in {self.filename}>"

    @abstractmethod
    def __init__(self, filename, **kwargs):
        """
        Initializing an error requires two pieces:
        * Store the relevant filename
        * Construct the error message from the kwargs
        """
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    @property
    def description(self):
        return self._description

    @property
    def level(self):
        return self._level.name

    @property
    def level_val(self):
        return self._level.value

    @property
    def name(self):
        return type(self).__name__

    @property
    def about(self):  # pragma: no cover
        return type(self).__doc__


class ClassDoesNotExist(ValueError):
    """Error raised when an xblock is allowed but not supported by the library"""
