# -*- coding: utf-8 -*-
"""
course.py

Object description for an OLX course tag
"""
from olxcleaner.objects.common import EdxObject, show_answer_list, randomize_list, show_correctness_list
from olxcleaner.parser.parser_exceptions import MissingFile, InvalidSetting
from olxcleaner.utils import check_static_file_exists, validate_graceperiod

class EdxCourse(EdxObject):
    """edX course object"""
    type = "course"
    depth = 0
    display_name = True

    # course pointer tags need three attributes:
    pointer_attr = {'url_name', 'course', 'org'}

    @property
    def allowed_children(self):
        return ["chapter", "wiki"]

    directory = None
    fullpath = None

    def savedir(self, directory, fullpath):
        """Saves the course directory and full path for future use"""
        self.directory = directory
        self.fullpath = fullpath

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        # Require some settings that need no further validation
        self.require_setting("org", errorstore)
        self.require_setting("course", errorstore)

        # Validate settings from the allowed list
        self.validate_entry_from_allowed("rerandomize", randomize_list, errorstore)
        self.validate_entry_from_allowed("show_correctness", show_correctness_list, errorstore)
        self.validate_entry_from_allowed("showanswer", show_answer_list, errorstore)

        # Handle start/end dates
        self.clean_date("start", errorstore, required=True)
        self.clean_date("end", errorstore, required=True)
        self.ensure_date_order(self.attributes.get("start"),
                               self.attributes.get("end"),
                               errorstore,
                               error_msg="start date must be before end date")

        # Handle enrollment_start/enrollment_end dates
        self.clean_date("enrollment_start", errorstore)
        self.clean_date("enrollment_end", errorstore)

        # Make sure there's a course image
        self.require_setting("course_image", errorstore)
        if self.attributes.get("course_image"):
            if not check_static_file_exists(self, self.attributes.get("course_image")):
                errorstore.add_error(MissingFile(self.filenames[-1],
                                                 edxobj=self,
                                                 missing_file=self.attributes.get("course_image")))

        # Check that the grace period is valid
        if not validate_graceperiod(self.attributes.get("graceperiod")):
            errorstore.add_error(InvalidSetting(self.filenames[-1],
                                                msg="Unable to recognize graceperiod format in policy."))

        # Ensure that the default number of attempts is None or positive
        self.require_positive_attempts(errorstore)
