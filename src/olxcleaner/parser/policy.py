# -*- coding: utf-8 -*-
"""
policy.py

Validation routines related to the policy file
"""
from olxcleaner.utils import traverse
from olxcleaner.parser.parser_exceptions import (
    MissingURLName,
    DuplicateURLName,
    BadPolicyFormat,
    PolicyRefNotFound,
    WrongObjectType,
    BadEntry,
    SettingOverride,
    GradingPolicyIssue
)

def find_url_names(course, errorstore):
    """
    Constructs a dictionary of (url_name: EdxObject) references

    :param course: EdxCourse object with a loaded course
    :param errorstore: ErrorStore object where errors are reported
    :return: Dictionary of {'url_name': EdxObject} links
    """
    results = {}

    # Traverse the tree
    for edxobj in traverse(course):
        url_name = edxobj.attributes.get('url_name')

        if url_name is None:
            if edxobj.needs_url_name and not edxobj.broken:
                # Report the error
                errorstore.add_error(MissingURLName(edxobj.filenames[0], edxobj=edxobj))
        else:
            # Record the name
            if url_name in results:
                # We have a collision!
                errorstore.add_error(DuplicateURLName(edxobj.filenames[0],
                                                      url_name=url_name,
                                                      tag1=results[url_name].type,
                                                      file1=results[url_name].filenames[0],
                                                      tag2=edxobj.type,
                                                      file2=edxobj.filenames[0]))
            else:
                results[url_name] = edxobj

    # Return the dictionary
    return results

def merge_policy(policy, url_names, errorstore):
    """
    Merges policy file data with course objects

    :param policy: Policy file json
    :param url_names: Dictionary of {urlname: EdxObject} pairings
    :param errorstore: ErrorStore object where errors are reported
    :return: None
    """
    if not isinstance(policy, dict):
        errorstore.add_error(BadPolicyFormat('policy.json'))
        return

    for entry in policy:
        # Split the entry into object type/url_name
        objtype, url_name = entry.split("/", 1)

        # Find the corresponding object in url_names
        edxobj = url_names.get(url_name, None)

        # Make sure we have an object
        if edxobj is None:
            errorstore.add_error(PolicyRefNotFound('policy.json', objtype=objtype, url_name=url_name))
            continue

        # Make sure the type matches
        if edxobj.type != objtype:
            errorstore.add_error(WrongObjectType('policy.json', objtype=objtype, objtypefound=edxobj.type, url_name=url_name))
            continue

        # Make sure the entry is a dictionary
        if not isinstance(policy[entry], dict):
            errorstore.add_error(BadEntry('policy.json', objtype=objtype, url_name=url_name))
            continue

        # Copy data into the object
        for element in policy[entry]:
            # Make sure we're not overwriting anything
            if element in edxobj.attributes:
                errorstore.add_error(SettingOverride('policy.json', objtype=objtype, url_name=url_name, setting=element))
                continue

            # Copy the data
            edxobj.attributes[element] = policy[entry][element]

def validate_grading_policy(grading_policy, errorstore):
    """
    Validates the grading policy of the course

    :param grading_policy: Grading policy file json
    :param errorstore: ErrorStore object where errors are reported
    :return: None
    """
    # Check the GRADER entry
    if "GRADER" not in grading_policy:
        errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg="'GRADER' entry not found in grading policy"))
    elif not isinstance(grading_policy["GRADER"], list):
        errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg="'GRADER' entry not in grading policy is not a list"))
    else:
        weightsum = 0
        types = set()
        # Validate the required components of each entry
        for idx, entry in enumerate(grading_policy["GRADER"]):
            if "drop_count" not in entry:
                msg = f"'drop_count' setting is omitted for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif not isinstance(entry['drop_count'], int):
                msg = f"'drop_count' setting is not an integer for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif entry['drop_count'] < 0:
                msg = f"'drop_count' setting is negative for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))

            if "min_count" not in entry:
                msg = f"'min_count' setting is omitted for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif not isinstance(entry['min_count'], int):
                msg = f"'min_count' setting is not an integer for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif entry['min_count'] < 1:
                msg = f"'min_count' setting is less than 1 for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))

            if "short_label" in entry and not isinstance(entry['short_label'], str):
                msg = f"'short_label' setting is not a string for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))

            if "type" not in entry:
                msg = f"'type' setting is omitted for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif not isinstance(entry['type'], str):
                msg = f"'type' setting is not a string for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            else:
                if entry['type'] in types:
                    msg = f"Assessment type '{entry['type']}' appears multiple times in the grading policy"
                    errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
                else:
                    types.add(entry['type'])

            if "weight" not in entry:
                msg = f"'weight' setting is omitted for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif not (isinstance(entry['weight'], int) or isinstance(entry['weight'], float)):
                msg = f"'weight' setting is not a number between 0 and 1 for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif entry['weight'] > 1 or entry['weight'] < 0:
                msg = f"'weight' setting is not a number between 0 and 1 for entry {idx+1} in the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            else:
                weightsum += entry['weight']

        # Check that weights add up to 100%
        if len(grading_policy["GRADER"]) == 0:
            msg = "GRADER entry in grading policy should not be empty"
            errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
        elif abs(weightsum - 1) > 1e-8:
            msg = "'weight' settings do not add up to 1"
            errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))

    # Check the GRADE_CUTOFFS entry
    if "GRADE_CUTOFFS" not in grading_policy:
        errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg="'GRADE_CUTOFFS' entry not found in grading policy"))
    elif not isinstance(grading_policy["GRADE_CUTOFFS"], dict):
        errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg="'GRADE_CUTOFFS' entry not in grading policy is not a dictionary"))
    else:
        # Object to entries that are not 'Pass', 'A', 'B', 'C', or 'D'
        clean = True
        for entry in grading_policy["GRADE_CUTOFFS"]:
            if entry in ['Pass', 'A', 'B', 'C', 'D']:
                # Validate the entries
                if not (isinstance(grading_policy["GRADE_CUTOFFS"][entry], int) or isinstance(grading_policy["GRADE_CUTOFFS"][entry], float)):
                    msg = f"'{entry}' entry is not a number in the GRADE_CUTOFFS part of the grading policy"
                    errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
                elif grading_policy["GRADE_CUTOFFS"][entry] > 1 or grading_policy["GRADE_CUTOFFS"][entry] < 0:
                    # We sometimes use 'Pass' < 0 to hide the pass line on the plot
                    if not (entry == 'Pass' and grading_policy["GRADE_CUTOFFS"][entry] < 0):
                        msg = f"'{entry}' entry is not between 0 and 1 in the GRADE_CUTOFFS part of the grading policy"
                        errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            else:
                clean = False
                msg = f"'{entry}' is not allowed in the GRADE_CUTOFFS part of the grading policy"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))

        if clean:
            if len(grading_policy["GRADE_CUTOFFS"]) == 0:
                # Make sure it's not empty
                msg = "GRADE_CUTOFFS entry in grading policy should not be empty"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif 'Pass' in grading_policy["GRADE_CUTOFFS"] and len(grading_policy["GRADE_CUTOFFS"]) > 1:
                # If we have a 'Pass' entry, make sure there's no letters too
                msg = "GRADE_CUTOFFS should have either 'Pass' or letters, not both"
                errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
            elif 'Pass' not in grading_policy["GRADE_CUTOFFS"]:
                # We're doing letter grades. Make sure they're all present and in order.
                if 'D' in grading_policy["GRADE_CUTOFFS"]:
                    required = ['A', 'B', 'C', 'D']
                elif 'C' in grading_policy["GRADE_CUTOFFS"]:
                    required = ['A', 'B', 'C']
                elif 'B' in grading_policy["GRADE_CUTOFFS"]:
                    required = ['A', 'B']
                else:
                    # We only have 'A'. Should be 'Pass' instead of 'A'.
                    required = ['A']
                    msg = "GRADE_CUTOFFS should use 'Pass' instead of 'A'"
                    errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
                current = 1.1
                for entry in required:
                    if entry not in grading_policy["GRADE_CUTOFFS"]:
                        # Make sure all higher letter grades are present
                        msg = f"GRADE_CUTOFFS is missing '{entry}'"
                        errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
                    elif grading_policy["GRADE_CUTOFFS"][entry] >= current:
                        # Make sure the cutoffs are decreasing in value
                        msg = f"GRADE_CUTOFFS is entry '{entry}' is not decreasing"
                        errorstore.add_error(GradingPolicyIssue('grading_policy.json', msg=msg))
                    else:
                        current = grading_policy["GRADE_CUTOFFS"][entry]
