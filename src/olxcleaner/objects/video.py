# -*- coding: utf-8 -*-
"""
video.py

Object description for an OLX video tag
"""
from olxcleaner.objects.common import EdxContent

class EdxVideo(EdxContent):
    """edX video object"""
    type = "video"
    can_be_empty = True
    display_name = True

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        # As video XML is such a mess with multiple formats, I'm not even going to try parsing it.
        # TODO: Validate video OLX
        pass
