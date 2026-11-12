# -*- coding: utf-8 -*-
"""
sequential.py

Object description for an OLX sequential tag
"""
from olxcleaner.objects.common import EdxObject, show_answer_list, randomize_list, show_correctness_list
from olxcleaner.parser.parser_exceptions import InvalidSetting

class EdxSequential(EdxObject):
    """edX sequential object"""
    type = "sequential"
    depth = 2
    display_name = True

    @property
    def allowed_children(self):
        return ['vertical']

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        self.validate_entry_from_allowed("rerandomize", randomize_list, errorstore)
        self.validate_entry_from_allowed("show_correctness", show_correctness_list, errorstore)
        self.validate_entry_from_allowed("showanswer", show_answer_list, errorstore)

        # Clean the start and due dates
        self.clean_date("start", errorstore)
        self.clean_date("due", errorstore)

        # Ensure dates fall in the correct order
        self.ensure_date_order(course.attributes.get("start"),
                               self.attributes.get("start"),
                               errorstore,
                               same_ok=True,
                               error_msg="start date cannot be before course start date")
        self.ensure_date_order(self.attributes.get("start"),
                               course.attributes.get("end"),
                               errorstore,
                               error_msg="start date must be before course end date")
        self.ensure_date_order(course.attributes.get("start"),
                               self.attributes.get("due"),
                               errorstore,
                               error_msg="due date must be after course start date")
        self.ensure_date_order(self.attributes.get("start"),
                               self.attributes.get("due"),
                               errorstore,
                               error_msg="start date must be before due date")
        self.ensure_date_order(self.attributes.get("due"),
                               course.attributes.get("end"),
                               errorstore,
                               same_ok=True,
                               error_msg="due date must be before course end date")

        # If this is a timed exam, make sure it's enabled in the policy
        if self.is_exam:
            if not course.attributes.get('enable_timed_exams'):
                msg = f"The tag {self} is a timed exam, but the course policy does not have 'enable_timed_exams=true'."
                errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))

    @property
    def is_exam(self):
        """Helper routine that determines whether or not this is a timed exam"""
        entry = self.attributes.get('is_time_limited')
        if entry == "true":
            return True
        return False
