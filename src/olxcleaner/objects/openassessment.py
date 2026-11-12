# -*- coding: utf-8 -*-
"""
openassessment.py

Object description for ORA assessments
"""
from olxcleaner.objects.common import EdxContent

class EdxORA(EdxContent):
    """edX openassessment object"""
    type = "openassessment"
    display_name = False
    can_be_pointer = False
    can_be_empty = False
    depth = 4

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        # There's a lot of structure here. We just want to validate the following date entries:
        #   <openassessment submission_start="2019-05-15T17:00:00" submission_due="2019-05-29T17:00:00">
        #     <assessments>
        #       <assessment start="2019-05-15T17:00:00" due="2019-06-05T17:00:00"/>
        #     </assessments>
        #   </openassessment>

        # Clean the start and due dates
        self.clean_date("submission_start", errorstore, required=True)
        self.clean_date("submission_due", errorstore, required=True)

        # Ensure dates fall in the correct order
        self.ensure_date_order(course.attributes.get("start"),
                               self.attributes.get("submission_start"),
                               errorstore,
                               same_ok=True,
                               error_msg="start date cannot be before course start date")
        self.ensure_date_order(self.attributes.get("submission_start"),
                               course.attributes.get("end"),
                               errorstore,
                               error_msg="start date must be before course end date")
        self.ensure_date_order(course.attributes.get("start"),
                               self.attributes.get("submission_due"),
                               errorstore,
                               error_msg="due date must be after course start date")
        self.ensure_date_order(self.attributes.get("submission_start"),
                               self.attributes.get("submission_due"),
                               errorstore,
                               error_msg="start date must be before due date")
        self.ensure_date_order(self.attributes.get("submission_due"),
                               course.attributes.get("end"),
                               errorstore,
                               same_ok=True,
                               error_msg="due date must be before course end date")

        # Find any assessments and check their dates
        for idx, assessment in enumerate(self.content.findall('./assessments/assessment')):
            # Process the dates into date objects
            startdate = assessment.get('start')
            duedate = assessment.get('due')
            startdate = self.convert2date(startdate, errorstore, f"assessment {idx + 1} start date")
            duedate = self.convert2date(duedate, errorstore, f"assessment {idx + 1} due date")

            # Now ensure the date orderings!
            # Note - these are not compared to the ORA dates, because they don't need to line up
            self.ensure_date_order(course.attributes.get("start"),
                                   startdate,
                                   errorstore,
                                   same_ok=True,
                                   error_msg=f"assessment {idx + 1} start date cannot be before course start date")
            self.ensure_date_order(startdate,
                                   course.attributes.get("end"),
                                   errorstore,
                                   error_msg=f"assessment {idx + 1} start date must be before course end date")
            self.ensure_date_order(course.attributes.get("start"),
                                   duedate,
                                   errorstore,
                                   error_msg=f"assessment {idx + 1} due date must be after course start date")
            self.ensure_date_order(startdate,
                                   duedate,
                                   errorstore,
                                   error_msg=f"assessment {idx + 1} start date must be before due date")
            self.ensure_date_order(duedate,
                                   course.attributes.get("end"),
                                   errorstore,
                                   same_ok=True,
                                   error_msg=f"assessment {idx + 1} due date must be before course end date")

            # TODO: Validate complete ORA schema
