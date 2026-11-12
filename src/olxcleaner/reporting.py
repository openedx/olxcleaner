# -*- coding: utf-8 -*-
"""
reporting.py

Contains methods used to report on an analyzed course
"""
from collections import Counter
from olxcleaner.utils import traverse
from olxcleaner.objects import EdxProblem, EdxSequential
from olxcleaner.exceptions import ErrorLevel

def report_statistics(course):
    """Report course statistics, formatted in a list."""
    result = []

    # If things are borked, then get out
    if course is None or course.broken:  # pragma: no cover
        return result

    # Compute statistics
    typecounter, exams, response_types, input_types, python_problems, problem_solutions = compute_statistics(course)

    # Now print to screen
    result.append("Number of each type of object:")
    for entry in typecounter:
        result.append(f"  - {entry}: {typecounter[entry]}")

    result.append(f"Number of exams: {exams}")

    if typecounter['problem'] > 0:
        result.append("Problem statistics:")
        result.append(f"    Number of problems: {typecounter['problem']}")
        result.append(f"    Number of problems with solutions: {problem_solutions}")
        result.append(f"    Number of problems with python scripts: {python_problems}")
        result.append(f"    response_types used*:")
        for entry in response_types:
            result.append(f"      - {entry}: {response_types[entry]}")
        result.append(f"    input_types used*:")
        for entry in input_types:
            result.append(f"      - {entry}: {input_types[entry]}")
        result.append(f"    * Multiple uses within a single problem only count once")

    return result

def compute_statistics(course):
    """
    Compute course statistics, returned in a number of variables.

    :param course: A validated course.
    :return: typecounter (dict),
             exams (int),
             response_types (dict),
             input_types (dict),
             python_problems (int),
             problem_solutions (int)
    """
    # Track how many of each type of object we have
    typecounter = Counter()

    # Track the number of sequentials that are time-limited (i.e., exams)
    exams = 0

    # Track the number of each type of response type and input type in problems
    response_types = Counter()
    input_types = Counter()

    # Track the number of problems using python scripts
    python_problems = 0

    # Track the number of problems with solutions
    problem_solutions = 0

    for edxobj in traverse(course):
        # Track the object type
        typecounter[edxobj.type] += 1

        if isinstance(edxobj, EdxSequential):
            # Check for exams
            if edxobj.is_exam:
                exams += 1

        elif isinstance(edxobj, EdxProblem):
            # Check for the 4 problem settings
            if edxobj.has_solution:
                problem_solutions += 1

            for response_type in edxobj.response_types:
                response_types[response_type] += 1

            for input_type in edxobj.input_types:
                input_types[input_type] += 1

            if 'python' in edxobj.scripts:
                python_problems += 1

    return typecounter, exams, response_types, input_types, python_problems, problem_solutions

def report_errors(errorstore):
    """Gives a simple report of all errors that were found, returned as a list"""
    result = []
    if errorstore.errors:
        for error in errorstore.errors:
            result.append((error.filename, f"{error.level} {error.name} ({error.filename}): {error.description}"))
    result.sort()  # Uses the filename for ordering
    wanted = [report for (filename, report) in result]
    return wanted

def report_error_summary(errorstore):
    """Reports summary statistics on the errors found, returned as a list"""
    result = ["Summary:"]
    counter = errorstore.summary()
    for level in ErrorLevel:
        if level.name in counter:
            result.append(f"{level.name}s: {sum(counter[level.name].values())}")
            for name, num in sorted(counter[level.name].items()):
                result.append(f"    {name}: {num}")
    if not counter:  # pragma: no cover
        result.append("No errors found!")
    return result

def construct_tree(course, maxdepth=None):
    """
    Constructs a tree version of the course structure, formatted as a list.

    :param course: EdxCourse object
    :param maxdepth: Maximum depth to display:
        0 = course
        1 = chapter
        2 = sequential
        3 = vertical
        4 = content
    :return: list containing tree structure
    """
    result = []
    _construct_tree(course, result, maxdepth)
    return result

def _construct_tree(obj, output, maxdepth, indent=0):
    """
    Recursively writes a tree version of the course structure to a list.

    :param obj: Current object to display
    :param output: List to append output to
    :param maxdepth: The maximum depth to display
    :param indent: Current indentation level (used in recursion)
    :return: None
    """
    if maxdepth is not None and obj.depth > maxdepth:
        return
    output.append(f'{" " * indent * 4}{obj}')
    for child in obj.children:
        _construct_tree(child, output, maxdepth, indent + 1)
