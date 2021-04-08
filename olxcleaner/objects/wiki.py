# -*- coding: utf-8 -*-
"""
wiki.py

Object description for an OLX wiki tag
"""
from olxcleaner.objects.common import EdxContent


class Wiki(EdxContent):
    """wiki object"""
    type = "wiki"
    can_be_empty = True
    display_name = True

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        # TODO: Validate wiki
        pass
