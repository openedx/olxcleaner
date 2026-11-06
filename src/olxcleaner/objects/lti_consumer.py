# -*- coding: utf-8 -*-
"""
lti_consumer.py

Object description for an OLX lti_consumer tag
"""
from olxcleaner.objects.common import EdxObject
from olxcleaner.parser.parser_exceptions import LTIError

class EdxLtiConsumer(EdxObject):
    """edX lti_consumer object"""
    can_be_pointer = False
    type = "lti_consumer"
    depth = 4
    can_be_empty = True
    display_name = True

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        # Check that required fields are present
        self.require_setting("lti_id", errorstore)
        if not self.attributes.get('hide_launch'):
            self.require_setting("launch_url", errorstore)

        # Check LTI passport exists in policy
        lti_id = self.attributes.get('lti_id')
        if lti_id:
            if not self.check_passports(course, lti_id):
                msg = f"Course policy does not include an 'lti_passports' entry for '{lti_id}', required for {self}."
                errorstore.add_error(LTIError(self.filenames[-1], msg=msg))

        # Check that lti_consumer is in the course policy as an advanced module
        if course.attributes.get('advanced_modules') is None or "lti_consumer" not in course.attributes.get('advanced_modules'):
            msg = f"Course policy does not include the 'lti_consumer' advanced module, required for {self}."
            errorstore.add_error(LTIError(self.filenames[-1], msg=msg))

    @staticmethod
    def check_passports(course, lti_id):
        """
        Checks to see if an LTI passport is in the course.
        
        :param course: The course object, which may contain settings relevant to the validation of this object
        :param lti_id: Passport to search for.
        :return: True if the passport is in the course, otherwise False.
        """
        for passport in course.attributes.get('lti_passports', []):
            if passport.startswith(lti_id + ":"):
                return True
        return False
