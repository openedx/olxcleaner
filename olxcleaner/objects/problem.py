# -*- coding: utf-8 -*-
"""
problem.py

Object description for an OLX problem tag
"""
from olxcleaner.objects.common import EdxContent, show_answer_list, randomize_list, show_correctness_list
from olxcleaner.parser.parser_exceptions import InvalidSetting

response_types = ['coderesponse', 'numericalresponse', 'formularesponse', 'customresponse', 'schematicresponse',
                  'externalresponse', 'imageresponse', 'optionresponse', 'symbolicresponse', 'stringresponse',
                  'choiceresponse', 'multiplechoiceresponse', 'truefalseresponse', 'annotationresponse',
                  'choicetextresponse']

input_types = ['optioninput', 'choicegroup', 'radiogroup', 'checkboxgroup', 'jsinput', 'textline', 'filesubmission',
               'codeinput', 'textbox', 'matlabinput', 'schematic', 'imageinput', 'crystallography', 'vsepr_input',
               'chemicalequationinput', 'formulaequationinput', 'drag_and_drop_input', 'editamoleculeinput',
               'designprotein2dinput', 'editageneinput', 'annotationinput', 'radiotextgroup', 'checkboxtextgroup']

class EdxProblem(EdxContent):
    """edX problem object"""
    type = "problem"
    display_name = True

    def __init__(self):
        # Do standard initialization
        super().__init__()
        # Add in extra objects
        self.scripts = []
        self.response_types = []
        self.input_types = []
        self.has_solution = False

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

        # Ensure that problem weight isn't negative
        weight = self.attributes.get("weight")
        if weight and float(weight) < 0:
            msg = f"The tag {self} has a negative problem weight."
            errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))

        # Ensure that number of attempts is None or positive
        self.require_positive_attempts(errorstore)

        # Detect scripts
        self.scripts = self.detect_scripts()

        # Detect response types
        self.response_types = self.detect_response_types()

        # Detect input types
        self.input_types = self.detect_input_types()

        # Detect solution
        self.has_solution = self.detect_solution()

    def detect_solution(self):
        """
        Find any solutions present in the problem

        :return: True/False
        """
        if self.content is None:
            return False

        # Does there exist at least one <solution> tag?
        if self.content.find('.//solution') is not None:
            return True
        return False

    def detect_response_types(self):
        """
        Locate and identify all response types used in the problem

        :return: List of response types used
        """
        tags = []
        if self.content is None:
            return []

        for rtype in response_types:
            # Does there exist at least one of these tags?
            if self.content.find('.//' + rtype) is not None:
                tags.append(rtype)
        return tags

    def detect_input_types(self):
        """
        Locate and identify all input types used in the problem

        :return: List of input types used
        """
        tags = []
        if self.content is None:
            return []

        for itype in input_types:
            # Does there exist at least one of these tags?
            if self.content.find('.//' + itype) is not None:
                tags.append(itype)
        return tags

    def detect_scripts(self):
        """
        Locate and identify the language of all scripts used in the problem

        :return: List of script languages used
        """
        # This code is modified from the edx-platform repository
        codetypes = set()
        if self.content is None:
            return []

        for script in self.content.findall('.//script'):
            stype = script.get('type')
            # Code is contained in script.text
            if stype:
                if 'javascript' in stype:
                    codetypes.add('javascript')
                    continue
                elif 'perl' in stype:
                    codetypes.add('perl')
                    continue
            # If not javascript or perl, we assume python (even if not present)
            codetypes.add('python')

        return list(codetypes)
