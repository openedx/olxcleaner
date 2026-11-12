# -*- coding: utf-8 -*-
"""
html.py

Object description for an OLX html tag
"""
from olxcleaner.objects.common import EdxContent

class EdxHtml(EdxContent):
    """edX html object"""
    type = "html"
    html_content = False  # Was the content set by slurping up an HTML file directly?
    # If True, content does not contain the wrapping html tag
    display_name = True

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        # Pretty much anything goes for an HTML file
        # Nothing to validate here
        pass
