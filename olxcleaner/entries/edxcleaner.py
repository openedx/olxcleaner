# -*- coding: utf-8 -*-
"""
edxcleaner.py

edX XML code validator, based on a very light wrapper around
the olxcleaner library. Despite the light touch, it
exposes all of the capabilities of the library.
"""
import sys
import argparse

from olxcleaner import validate
from olxcleaner.__version__ import version
from olxcleaner.reporting import construct_tree, report_errors, report_error_summary, report_statistics
from olxcleaner.loader.xml_exceptions import CourseXMLDoesNotExist


def handle_arguments():
    """Look after all command-line arguments"""
    parser = argparse.ArgumentParser(description="edX XML cleaner -- A validator for XML edX courses")

    # Required arguments
    # Location of course.xml
    parser.add_argument("-c", "--course", help="Location of course.xml (default=./course.xml)", default="course.xml")

    # Optional arguments
    # Output file for structure
    parser.add_argument("-t", "--tree", help="File to output course structure to")

    # Level to output structure to
    parser.add_argument("-l", "--level", help="Depth level to output structure to",
                        default=4, choices=[0, 1, 2, 3, 4], type=int)

    # Quiet mode
    parser.add_argument("-q", "--quiet", help="Quiet mode (no screen output)", action="store_true")

    # Error output
    parser.add_argument("-e", "--noerrors", help="Suppress error output", action="store_true")

    # Error summary
    parser.add_argument("-s", "--nosummary", help="Suppress error summary", action="store_true")

    # Error summary
    parser.add_argument("-S", "--stats", help="Output course statistics", action="store_true")

    # Failure level
    parser.add_argument("-f", "--failure", default=3, choices=[0, 1, 2, 3, 4], type=int,
                        help="Level of errors at which to declare failure: 0=DEBUG, 1=INFO, "
                             "2=WARNING, 3=ERROR (default), 4=NEVER")

    # Steps to run
    parser.add_argument("-p", "--steps", default=8, choices=[1, 2, 3, 4, 5, 6, 7, 8], type=int,
                        help="Validation steps to take: 1=load course, 2=load policies, 3=check url_names, "
                             "4=validate policy, 5=validate grading policy, 6=validate tags, "
                             "7=perform global validation, 8=perform detailed global validation (default)")

    # Ignore list
    parser.add_argument('-i', '--ignore', nargs='+', help='List of errors to ignore')

    # Parse the command line
    return parser.parse_args()


def main():
    """Entry point for command line instantiation"""
    # Read the command line arguments
    args = handle_arguments()

    if not args.quiet:
        print(f'edX XML cleaner {version} -- A validator for XML edX courses')
        print(f'Loading...')

    # Validate the course
    course, errorstore, url_names = validate(args.course, args.steps, args.ignore)

    # Check that the course exists
    if len(errorstore.errors) > 0 and isinstance(errorstore.errors[0], CourseXMLDoesNotExist):
        print(f"Error: {errorstore.errors[0].description}")
        sys.exit(1)

    # Output reports
    if not args.quiet:
        print(f'Loaded from {course.fullpath}')

        if not args.noerrors:
            error_report = report_errors(errorstore)
            if error_report:
                print()
                for line in error_report:
                    print(line)
        if not args.nosummary:
            print()
            for line in report_error_summary(errorstore):
                print(line)
        if args.stats:
            print()
            for line in report_statistics(course):
                print(line)

    # Output the structure to file
    if args.tree and course is not None:
        if not args.quiet:
            print()
            print(f"Writing structure to {args.tree}")
        with open(args.tree, 'w') as f:
            for line in construct_tree(course, args.level):
                f.write(line + "\n")

    # Exit with the appropriate error level
    if errorstore.return_error(args.failure):
        if not args.quiet:
            print()
            print(f"Done! Exiting with code 1")
        sys.exit(1)
    else:
        if not args.quiet:
            print()
            print(f"Done! Exiting with code 0")
        sys.exit(0)

if __name__ == '__main__':
    main()
