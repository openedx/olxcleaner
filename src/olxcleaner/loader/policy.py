# -*- coding: utf-8 -*-
"""
policyloader.py

Routines to load the policy files of an edX course
"""
import os
from os.path import isfile
import json
from olxcleaner.loader.policy_exceptions import (
    NoRunName,
    PolicyNotFound,
    BadPolicy
)

default_grading_policy = {
    "GRADER": [
        {
            "drop_count": 0,
            "min_count": 1,
            "short_label": "HW",
            "type": "Homework",
            "weight": 1
        },
    ],
    "GRADE_CUTOFFS": {
        "Pass": 0.5
    }
}

def load_policy(directory, course, errorstore):
    """
    Loads the policy file for a course. If loading fails, empty
    dictionaries are returned.

    :param directory: Path for course.xml (or equivalent)
    :param course: EdxCourse object from parsed course
    :param errorstore: ErrorStore object to store errors
    :return: policy, grading_policy objects
    """
    # Get the run name for the course
    runname = course.attributes.get("url_name")
    if runname is None:
        errorstore.add_error(NoRunName(course.filenames[0]))
        return {}, {}

    # Construct filenames for policy files
    policyfile = os.path.join("policies", runname, "policy.json")
    gradingfile = os.path.join("policies", runname, "grading_policy.json")

    # Load the policy files
    policy = load_json(directory, policyfile, errorstore)
    grading_policy = load_json(directory, gradingfile, errorstore)
    if not grading_policy:
        grading_policy = default_grading_policy

    # Return the results
    return policy, grading_policy

def load_json(directory, filename, errorstore):
    """
    Load json from a file, storing any loading errors in the errorstore

    :param directory: Course directory
    :param filename: File to load
    :param errorstore: ErrorStore object to store errors
    :return: Contents of json file
    """
    fullfile = os.path.join(directory, filename)

    if not isfile(fullfile):
        errorstore.add_error(PolicyNotFound(filename))
        return {}

    try:
        with open(fullfile) as f:
            return json.load(f)
    except json.decoder.JSONDecodeError as err:
        errorstore.add_error(BadPolicy(filename, msg=str(err)))
        return {}
