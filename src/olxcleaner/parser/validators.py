# -*- coding: utf-8 -*-
"""
validators.py

Validation routines that act on the course as a whole
"""
import inspect
from abc import ABC, abstractmethod
from olxcleaner.objects import EdxDiscussion
from olxcleaner.utils import traverse
from olxcleaner.parser.parser_exceptions import (
    MissingDisplayName,
    ExtraDisplayName,
    DuplicateID
)

class GlobalValidator(ABC):
    """
    Abstract base class describing global validation routines.
    Only the __call__ method needs to be implemented.
    """

    @abstractmethod
    def __call__(self, course, errorstore, url_names):
        """
        Abstract method to perform validation

        :param course: EdxCourse object with a loaded course
        :param errorstore: ErrorStore object where errors are reported
        :param url_names: Dictionary of url_name to objects
        :return: None
        """

    @classmethod
    def validators(cls):
        """
        Yield an iterable of instances of immediate subclasses of this class
        """
        for child in cls.__subclasses__():
            # Only attempt instantiation if not an abstract base class
            if not inspect.isabstract(child):
                yield child()

class CheckDisplayNames(GlobalValidator):
    """Searches the course for missing display_name attributes"""

    def __call__(self, course, errorstore, url_names):
        for edxobj in traverse(course):
            display_name = edxobj.attributes.get('display_name')
            if edxobj.display_name is True and (display_name is None or display_name == ""):
                errorstore.add_error(MissingDisplayName(edxobj.filenames[-1], edxobj=edxobj))
            elif edxobj.display_name is False and display_name is not None:
                errorstore.add_error(ExtraDisplayName(edxobj.filenames[-1], edxobj=edxobj))

class CheckDiscussionIDs(GlobalValidator):
    """Searches the course for duplicate discussion_id entries in discussion blocks"""

    def __call__(self, course, errorstore, url_names):
        discussion_ids = {}
        for edxobj in traverse(course):
            if isinstance(edxobj, EdxDiscussion):
                disc_id = edxobj.attributes.get('discussion_id')
                if disc_id:
                    if disc_id in discussion_ids:
                        errorstore.add_error(DuplicateID(edxobj.filenames[-1],
                                                         edxobj1=edxobj,
                                                         edxobj2=discussion_ids[disc_id],
                                                         disc_id=disc_id))
                    else:
                        discussion_ids[disc_id] = edxobj
