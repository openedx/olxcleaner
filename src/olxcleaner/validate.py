# -*- coding: utf-8 -*-
"""
validate.py

Workhorse function that validates an OLX course
"""
import os

from olxcleaner.errorstore import ErrorStore
from olxcleaner.loader import load_course, load_policy
from olxcleaner.parser.policy import (find_url_names, merge_policy,
                                      validate_grading_policy)
from olxcleaner.parser.slowvalidators import SlowValidator
from olxcleaner.parser.validators import GlobalValidator
from olxcleaner.utils import traverse

from olxcleaner.objects.common import EdxObject


def validate(filename, steps=8, ignore=None, allowed_xblocks=None):
    """
    Validate an OLX course by performing the given number of steps:

      * 1: Load the course
      * 2: Load the policy and grading policy
      * 3: Validate url_names
      * 4: Merge policy data with course, ensuring that all references are valid
      * 5: Validate the grading policy
      * 6: Have every object validate itself
      * 7: Parse the course for global errors
      * 8: Parse the course for global errors that may be time-consuming to detect

    :param filename: Location of course xml file or directory
    :param steps: Number of validation steps to take (1 = first only, 8 = all)
    :param ignore: List of errors to ignore
    :param allowed_xblocks: List of all allowed xblocks.
    :return: course object, errorstore object, url_names dictionary (or None if steps < 3)
    """
    if allowed_xblocks is not None:
        supported_xblocks = {cls.type for cls in EdxObject.get_subclasses()}
        allowed_xblocks = set(allowed_xblocks) - supported_xblocks

    # Create an error store
    if ignore is None:
        ignore = []
    errorstore = ErrorStore(ignore)

    # Validation Step #1: Load the course
    if os.path.isdir(filename):
        directory = os.path.join(filename)
        file = "course.xml"
    else:
        directory, file = os.path.split(filename)

    course = load_course(directory, file, errorstore, allowed_xblocks)
    if not course:
        return None, errorstore, None

    if steps > 1:
        # Validation Step #2: Load the policy files
        policy, grading_policy = load_policy(directory, course, errorstore)

    url_names = None
    if steps > 2:
        # Validation Step #3: Construct a dictionary of url_names
        url_names = find_url_names(course, errorstore)

    if steps > 3:
        # Validation Step #4: Merge policy data into object attributes
        merge_policy(policy, url_names, errorstore)

    if steps > 4:
        # Validation Step #5: Validate grading policy
        validate_grading_policy(grading_policy, errorstore)

    if steps > 5:
        # Validation Step #6: Have every object validate itself
        for edxobj in traverse(course):
            edxobj.validate(course, errorstore)

    if steps > 6:
        # Validation Step #7: Parse the course for global errors
        for validator in GlobalValidator.validators():
            validator(course, errorstore, url_names)

    if steps > 7:
        # Validation Step #8: Parse the course for global errors that are time-consuming to detect
        for validator in SlowValidator.validators():
            validator(course, errorstore, url_names)

    return course, errorstore, url_names
