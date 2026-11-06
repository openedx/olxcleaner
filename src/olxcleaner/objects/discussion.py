# -*- coding: utf-8 -*-
"""
discussion.py

Object description for an OLX discussion tag
"""
from olxcleaner.objects.common import EdxObject
from olxcleaner.parser.parser_exceptions import Obsolete

class EdxDiscussion(EdxObject):
    """edX discussion object"""
    type = "discussion"
    depth = 4
    can_be_empty = True
    needs_url_name = False
    display_name = 'optional'

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        # Check for obsolete invocation
        if len(self.filenames) == 2:
            msg = f"The tag {self} should be included inline rather than through the discussion directory."
            errorstore.add_error(Obsolete(self.filenames[0], msg=msg))

        # Check for required attributes
        self.require_setting("discussion_id", errorstore)
        self.require_setting("discussion_category", errorstore)
        self.require_setting("discussion_target", errorstore)
