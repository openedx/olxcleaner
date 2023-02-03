# -*- coding: utf-8 -*-
"""
common.py

Contains abstract base classes to describe various edX objects
"""
from abc import ABC, ABCMeta, abstractmethod

import dateutil.parser
import pytz

from olxcleaner.exceptions import ClassDoesNotExist
from olxcleaner.parser.parser_exceptions import DateOrdering, InvalidSetting


class EdxObject(ABC):
    """Abstract base class for edX structure objects"""

    def __init__(self):
        """Initialize storage"""
        # Stores the children objects of this object
        self.children = []

        # Stores the attributes of this object
        self.attributes = {}

        # Stores the filenames associated with this object
        # If this file is loaded using a url_name pointer, will
        # contain two entries: [pointerfile, contentfile]
        # If not, will just contain one entry: [contentfile]
        self.filenames = []

    # Default settings

    # Can this object store content?
    content_store = False

    # Can this object be referenced using pointer tags? (if True, then can be located in the directory of the appropriate type)
    can_be_pointer = True
    # What attributes are needed to be a pointer tag?
    pointer_attr = {'url_name'}

    # What depth does this object typically appear at? (used for reporting)
    depth = 0

    # What is the name of the tag? (also the directory that stores this content type)
    type = None

    # Can this tag be empty?
    can_be_empty = False

    # Does this tag need a display_name attribute? Options are True, False and 'optional'
    display_name = False

    # Does this tag need a url_name attribute?
    needs_url_name = True

    # Is this element broken (and hence needs no further errors reported?)
    broken = False

    # Who is my parent?
    parent = None

    @property
    def allowed_children(self):  # pragma: no cover
        """
        What children object types can this object contain?
        Note: implemented as property to avoid forward reference problems.
        """
        return []

    def add_child(self, node):
        """Adds a child to this object"""
        self.children.append(node)
        # Mark the node's parent so that we can go up and down the chain of objects
        node.parent = self

    def add_attribs(self, attribs):
        """Adds to the attributes for this object"""
        self.attributes.update(attribs)

    def add_filename(self, value):
        """Adds a filename to the filename list for this object"""
        self.filenames.append(value)

    def __repr__(self):
        """Produce a string representation of this object"""
        name = self.attributes.get("display_name")
        url_name = self.attributes.get("url_name")
        result = f"<{self.type}"
        if url_name:
            result += f" url_name='{url_name}'"
        if name:
            result += f" display_name='{name}'"
        result += ">"
        return result

    def is_pointer(self, attribs=None):
        """
        Returns True if the attributes for this object imply that it
        is a pointer object, pointing to a new file

        Uses attribs if passed in, or self.attributes if not
        """
        if attribs is None:  # pragma: no cover
            attribs = self.attributes
        # Follows pointer convention in edX: is_pointer_tag in
        # https://github.com/openedx/edx-platform/blob/master/xmodule/x_module.py
        # Also needs to have no children and no text (not tested)
        return set(attribs.keys()) == self.pointer_attr and self.can_be_pointer

    @abstractmethod
    def validate(self, course, errorstore):  # pragma: no cover
        """
        Perform validation on this object.

        Objects should validate their contents other than those tags
        contained in allowed_children.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        pass

    # List of subclasses of EdxObject
    _subclasses = []

    @staticmethod
    def get_subclasses():
        """Get a list of all subclasses"""
        subclasses = set()
        work = [EdxObject]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return list(subclasses)

    @staticmethod
    def get_object(object_type):
        """
        Returns a class instance that has type object_type

        :param object_type: type parameter for the desired class
        :return: Class with type object_type
        """
        # If it doesn't already exist, construct the list of subclasses
        if not EdxObject._subclasses:
            EdxObject._subclasses = EdxObject.get_subclasses()

        for cls in EdxObject._subclasses:
            if cls.type == object_type:
                return cls()
        raise ClassDoesNotExist(f"Cannot instantiate object of unknown type <{object_type}>")  # pragma: no cover

    def validate_entry_from_allowed(self, setting_name, allowed_list, errorstore, missing_ok=True):
        """
        Validate that the entry under the setting setting_name for this object is in the allowed list.
        If not, put the error in the errorstore.

        :param setting_name: The name of the setting
        :param allowed_list: List of allowed entries
        :param errorstore: ErrorStore object to store errors
        :param missing_ok: Whether the entry can be missing
        :return: None
        """
        # Check the entry
        entry = self.attributes.get(setting_name)
        if entry is None:
            if not missing_ok:  # pragma: no cover
                msg = f"The tag {self} does not have the required setting '{setting_name}'."
                errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))
            return
        elif entry not in allowed_list:
            msg = f"The tag {self} has an invalid setting '{setting_name}={entry}'."
            errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))

    def require_setting(self, setting_name, errorstore):
        """
        Validate that the setting setting_name has an entry for this object.
        If not, put the error in the errorstore.

        :param setting_name: The name of the setting
        :param errorstore: ErrorStore object to store errors
        :return: None
        """
        # Check the entry
        entry = self.attributes.get(setting_name)
        if entry is None:
            msg = f"The tag {self} does not have the required setting '{setting_name}'."
            errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))

    def clean_date(self, setting_name, errorstore, required=False):
        """
        Clean the date entry in setting_name, storing it.
        If invalid, report the error, and nullify the entry.

        :param setting_name: The name of the setting
        :param errorstore: ErrorStore object to store errors
        :param required: Whether or not this setting is required
        :return: None
        """
        # Handle the required part
        if required:
            self.require_setting(setting_name, errorstore)

        # Handle the cleaning part
        # Done in a separate routine, so that that routine can be called when we don't want to overwrite setting
        date = self.attributes.get(setting_name)
        self.attributes[setting_name] = self.convert2date(date, errorstore, setting_name)

    def convert2date(self, date, errorstore, setting_name):
        """
        Returns a date interpretation of the given date.
        If there's an issue, store it in the errorstore, using setting_name in the error message.
        """
        if date is None:
            return None

        # Make sure it parses properly
        try:
            parsed_date = dateutil.parser.parse(date)
            if parsed_date.tzinfo is None or parsed_date.tzinfo.utcoffset(parsed_date) is None:
                # Apply a timezone to the date
                return pytz.utc.localize(parsed_date)
            else:
                # Shift to UTC
                return parsed_date.astimezone(pytz.utc)
        except (TypeError, ValueError):
            msg = f"The tag {self} has an invalid date setting for {setting_name}: '{date}'."
            errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))
            return None

    def ensure_date_order(self, date1, date2, errorstore, error_msg, same_ok=False):
        """
        Ensures that the dates appear in order date1 < date2. If not, stores msg as an error in errorstore.
        If either date is None, no comparison is made.

        :param date1: First date to compare
        :param date2: Second date to compare
        :param errorstore: ErrorStore object to store errors
        :param error_msg: The message to report
        :param same_ok: Whether or not it's ok for the dates to be the same
        :return: None
        """
        if date1 is None or date2 is None:
            return

        # Check the ordering
        if same_ok:
            if date1 > date2:
                msg = f"The tag {self} has a date out of order: {error_msg}"
                errorstore.add_error(DateOrdering(self.filenames[-1], msg=msg))
        else:
            if date1 >= date2:
                msg = f"The tag {self} has a date out of order: {error_msg}"
                errorstore.add_error(DateOrdering(self.filenames[-1], msg=msg))

    def require_positive_attempts(self, errorstore):
        """
        Require that the object's "attempts" attribute is positive.

        :param errorstore: ErrorStore to report any errors
        :return: None
        """
        attempts = self.attributes.get("attempts")
        try:
            if attempts and int(attempts) < 1:
                msg = f"The tag {self} should have a positive number of attempts."
                errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))
        except ValueError:
            msg = f"The tag {self} should have a positive number of attempts."
            errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))


class EdxContent(EdxObject, metaclass=ABCMeta):
    """Abstract class for edX content objects"""

    # Can this object store content?
    content_store = True

    # What depth does this object typically appear at? (used for reporting)
    depth = 4

    # Contains the content of the tag, including the tag itself (except for HTML tags that reference an html file)
    content = None


# Collections of constants
show_answer_list = ["always", "answered", "attempted", "closed", "finished", "correct_or_past_due",
                    "past_due", "never", "after_attempts"]

randomize_list = ["always", "onreset", "never", "per_student"]

show_correctness_list = ['always', 'past_due', 'never']
