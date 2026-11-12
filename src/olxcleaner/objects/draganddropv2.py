# -*- coding: utf-8 -*-
"""
draganddropv2.py

Object description for the "new" drag and drop interface
"""
import json
from olxcleaner.objects.common import EdxObject
from olxcleaner.parser.parser_exceptions import InvalidSetting

class EdxDragAndDropV2(EdxObject):
    """edX drag-and-drop-v2 object"""
    type = "drag-and-drop-v2"
    display_name = 'optional'
    can_be_pointer = False
    can_be_empty = True
    depth = 4

    def __init__(self):
        # Do standard initialization
        super().__init__()
        # Add in extra objects
        self.parsed_data = {}

    def validate(self, course, errorstore):
        """
        Perform validation on this object.

        :param course: The course object, which may contain settings relevant to the validation of this object
        :param errorstore: An ErrorStore object to which errors should be reported
        :return: None
        """
        # The data for this Xblock is exported as json in the data field
        datafields = self.attributes.get('data')
        if datafields is None:
            return

        # Make sure that the field is valid, and save it for future validation
        try:
            parsed_data = json.loads(datafields)
            self.parsed_data = parsed_data
            if not isinstance(self.parsed_data, dict):
                msg = f"The tag {self} data JSON is not a dictionary."
                errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))
        except json.decoder.JSONDecodeError as err:
            msg = f"The tag {self} has an error in the data JSON: {err}."
            errorstore.add_error(InvalidSetting(self.filenames[-1], msg=msg))
            return
