# -*- coding: utf-8 -*-
"""
parsing_exceptions.py

Contains exception definitions for global course parsing
"""
from olxcleaner.exceptions import CourseError, ErrorLevel

class MissingURLName(CourseError):
    """A tag is missing the `url_name` attribute. edX will provide a garbage 32-character name for you, but everything is cleaner if you provide a nice name yourself."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The tag {kwargs['edxobj']} has no url_name."

class DuplicateURLName(CourseError):
    """Two tags have the same `url_name` attribute. This can lead to the wrong content loading, and seriously impedes this program's error analysis."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = (f"Duplicate url_name found: '{kwargs['url_name']}' appears as <{kwargs['tag1']}> in "
                             f"{kwargs['file1']} and also as <{kwargs['tag2']}> in {kwargs['file2']}")

class MissingDisplayName(CourseError):
    """A tag is missing the `display_name` attribute. edX will fill a generic name for you."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The tag {kwargs['edxobj']} is missing the display_name attribute."

class ExtraDisplayName(CourseError):
    """A tag has a `display_name` attribute when it shouldn't."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The tag {kwargs['edxobj']} has an erroneous display_name attribute."

class BadPolicyFormat(CourseError):
    """The policy file didn't have the expected structure."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The policy file is not a dictionary of values"

class PolicyRefNotFound(CourseError):
    """The policy file references an object that doesn't exist."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The policy file refers to <{kwargs['objtype']} url_name='{kwargs['url_name']}'> which does not exist in the course structure"

class WrongObjectType(CourseError):
    """The policy file references an object of one type, but that object is found in the course with another type."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The policy file refers to a <{kwargs['objtype']}> tag with url_name '{kwargs['url_name']}'. However, that url_name points to a <{kwargs['objtypefound']}> tag."

class BadEntry(CourseError):
    """The policy file contains an entry that is not a dictionary."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The policy file entry for <{kwargs['objtype']} url_name='{kwargs['url_name']}'> is not a dictionary"

class SettingOverride(CourseError):
    """The policy file is overriding a setting specified in a file."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The policy file entry for <{kwargs['objtype']} url_name='{kwargs['url_name']}'> is overriding the setting for '{kwargs['setting']}'"

class GradingPolicyIssue(CourseError):
    """A catch-all error for issues in the grading policy."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = kwargs['msg']

class InvalidSetting(CourseError):
    """A setting has been set to an invalid value."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = kwargs['msg']

class DateOrdering(CourseError):
    """A date setting appears out of order with another date setting."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = kwargs['msg']

class Obsolete(CourseError):
    """The way this object has been set up is obsolete."""
    _level = ErrorLevel.INFO

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = kwargs['msg']

class LTIError(CourseError):
    """There appears to be an error in the way that an LTI component is being invoked."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = kwargs['msg']

class MissingFile(CourseError):
    """A file appears to be missing from the static directory."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag contains a reference to a missing static file: {kwargs['missing_file']}"

class BadJumpToLink(CourseError):
    """An internal jump_to_id link points to a url_name that doesn't exist."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag contains a link to a url_name that doesn't exist: {kwargs['link']}"

class BadCourseLink(CourseError):
    """An internal /course/ link points to a location that doesn't exist."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag contains a link to a location that doesn't exist: {kwargs['link']}"

class DuplicateID(CourseError):
    """A discussion ID is duplicated. This leads to the discussion forums randomly telling students that threads have been deleted."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj1']} tag and the {kwargs['edxobj1']} tag both use the same discussion id: {kwargs['disc_id']}"
