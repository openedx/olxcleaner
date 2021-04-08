# -*- coding: utf-8 -*-
"""
xml_exceptions.py

Contains exception definitions for XML loading
"""
from olxcleaner.exceptions import CourseError, ErrorLevel

class CourseXMLDoesNotExist(CourseError):
    """The supplied `course.xml` file does not exist (or could not be opened)."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The file '{filename}' does not exist."

class InvalidXML(CourseError):
    """The specified XML file has a syntax error."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = kwargs['error']

class InvalidHTML(CourseError):
    """The specified HTML file has a syntax error."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = kwargs['error']

class CourseXMLName(CourseError):
    """The master file was not called `course.xml`."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The course file, {filename}, is not named course.xml"

class TagMismatch(CourseError):
    """A file purporting to contain a specific tag type (e.g., `problem` or `chapter`) instead contains a different tag."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = (f"The file is of type <{kwargs['tag1']}> but "
                             f"opens with a <{kwargs['tag2']}> tag")

class EmptyTag(CourseError):
    """A tag was unexpectedly empty (e.g., a `chapter` tag had no children)."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag is unexpectedly empty"

class ExtraURLName(CourseError):
    """A tag that had been pointed to by `url_name` from another file has a `url_name` of its own."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The opening <{kwargs['tag']}> tag shouldn't have a url_name attribute"

class InvalidPointer(CourseError):
    """This tag appears to be trying to point to another file, but contains unexpected attributes, and is hence not pointing."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag looks like it is an invalid pointer tag"

class FileDoesNotExist(CourseError):
    """The file being pointed to does not exist."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag points to the file {kwargs['new_file']} that does not exist"

class SelfPointer(CourseError):
    """A tag appears to be pointing to itself."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The tag {kwargs['edxobj']} tag appears to be pointing to itself"

class UnexpectedTag(CourseError):
    """A tag was found in an inappropriate location (e.g., a `vertical` in a `chapter`), or the tag was not recognized."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"A <{kwargs['tag']}> tag was unexpectedly found inside the {kwargs['edxobj']} tag"

class PossiblePointer(CourseError):
    """This tag looks like it isn't a pointer tag, but a file exists that it could be trying to point to. (This file is thus orphaned, as no other tag can point to it due to `url_name` clashes.)"""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = (f"The {kwargs['edxobj']} tag "
                             f"is not a pointer, but a file that it could point to exists ({kwargs['new_file']})")

class PossibleHTMLPointer(CourseError):
    """This HTML tag looks like it isn't a pointer tag, but a file exists that it could be trying to point to."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = (f"The {kwargs['edxobj']} tag "
                             f"is not a pointer, but a file that it could point to exists ({kwargs['new_file']})")

class UnexpectedContent(CourseError):
    """A tag contains unexpected text content."""
    _level = ErrorLevel.ERROR

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag should not contain any text ({kwargs['text'].strip()[:15]}...)"

class NonFlatURLName(CourseError):
    """A `url_name` pointer uses colon notation to point to a subdirectory. While partially supported, this is not recommended."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag uses obsolete colon notation in the url_name to point to a subdirectory"

class NonFlatFilename(CourseError):
    """A filename pointer for an HTML file uses colon notation to point to a subdirectory. While partially supported, this is not recommended."""
    _level = ErrorLevel.WARNING

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = f"The {kwargs['edxobj']} tag uses obsolete colon notation to point to a subdirectory for filename {kwargs['newfilename']}"

class DuplicateHTMLName(CourseError):
    """Two HTML tags point to the same HTML file (`filename` attribute). While this isn't obviously problematic, probably best not to do it."""
    _level = ErrorLevel.INFO

    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self._description = (f"Two html tags refer to the same HTML file (using the 'filename' attribute): "
                             f"{kwargs['htmlfilename']} is referenced in {filename} and {kwargs['file2']}")
