"""
test_validate.py

Tests the full validation pipeline
"""
from tests.helpers import assert_caught_all_errors, assert_error, assert_not_error
from tests.test_load_policy import handle_course1_errors
from tests.test_load_xml import handle_course2_errors, handle_nocourse_errors
from tests.test_parser import handle_course7_errors
from tests.test_validators import (handle_discussion_id_errors_in_10,
                                   handle_display_name_errors_in_10,
                                   handle_general_errors_in_10,
                                   handle_link_errors_in_10)

from olxcleaner import validate
from olxcleaner.loader.xml_exceptions import UnexpectedTag
from olxcleaner.parser.parser_exceptions import (DateOrdering, InvalidSetting,
                                                 LTIError, MissingFile,
                                                 MissingURLName, Obsolete)


def test_validate_nocourse():
    course, errorstore, url_names = validate("testcourses/nocourse.xml", 2)
    handle_nocourse_errors(errorstore)
    assert_caught_all_errors(errorstore)


def test_validate_course1():
    course, errorstore, url_names = validate("testcourses/testcourse1", 2)
    handle_course1_errors(errorstore)
    assert_caught_all_errors(errorstore)


def test_validate_course2():
    course, errorstore, url_names = validate("testcourses/testcourse2/coursefile.xml", 1)
    handle_course2_errors(errorstore)
    assert_caught_all_errors(errorstore)


def test_validate_course2_wiki_xblock_is_supported():
    """
    Test validate for course with wiki
    :return:
    """
    course, errorstore, url_names = validate("testcourses/testcourse2/coursefile.xml", 1)
    assert_not_error(errorstore, UnexpectedTag, 'course/mycourseurl.xml',
                 "A <wiki> tag was unexpectedly found inside the <course url_name='mycourseurl'> tag")


def test_validate_course7():
    course, errorstore, url_names = validate("testcourses/testcourse7/course.xml", 5)
    handle_course7_errors(errorstore)
    assert_caught_all_errors(errorstore)


def test_validate_course8():
    """This test includes individual component validation. Almost everything should pass."""
    course, errorstore, url_names = validate("testcourses/testcourse8", 6)
    assert_error(errorstore, InvalidSetting, 'course/mycourseurl.xml',
                 "The tag <course url_name='mycourseurl'> does not have the required setting 'course_image'.")
    assert_caught_all_errors(errorstore)


def test_validate_course9():
    """This test includes individual component validation. This similar to course8, but riddled with errors."""
    course, errorstore, url_names = validate("testcourses/testcourse9", 6)
    assert_error(errorstore, InvalidSetting, 'course/mycourseurl.xml',
                 "Unable to recognize graceperiod format in policy.")
    assert_error(errorstore, InvalidSetting, 'problem/problem.xml',
                 "The tag <problem url_name='problem'> has an invalid setting 'showanswer=bad'.")
    assert_error(errorstore, InvalidSetting, 'chapter/chapter.xml',
                 "The tag <chapter url_name='chapter' display_name='Hi there!'> has an invalid date setting for start: 'Feb 20, 2019, 17:00zzz'.")
    assert_error(errorstore, DateOrdering, 'sequential/sequential.xml',
                 "The tag <sequential url_name='sequential' display_name='Hi there!'> has a date out of order: start date cannot be before course start date")
    assert_error(errorstore, DateOrdering, 'vertical/vertical.xml',
                 "The tag <vertical url_name='vertical' display_name='Hi mom!'> has a date out of order: due date must be before course end date")
    assert_error(errorstore, DateOrdering, 'problem/problem.xml',
                 "The tag <problem url_name='problem'> has a date out of order: start date must be before due date")
    assert_error(errorstore, MissingURLName, 'vertical/vertical.xml',
                 "The tag <problem display_name='no url_name'> has no url_name.")
    assert_error(errorstore, InvalidSetting, 'vertical/vertical.xml',
                 "The tag <problem display_name='no url_name'> has an invalid setting 'showanswer=hah!'.")
    assert_error(errorstore, DateOrdering, 'vertical/vertical.xml',
                 "The tag <problem display_name='no url_name'> has a date out of order: due date must be before course end date")
    assert_error(errorstore, Obsolete, 'vertical/vertical.xml',
                 "The tag <discussion url_name='discussion'> should be included inline rather than through the discussion directory.")
    assert_error(errorstore, InvalidSetting, 'discussion/discussion.xml',
                 "The tag <discussion url_name='discussion'> does not have the required setting 'discussion_id'.")
    assert_error(errorstore, InvalidSetting, 'discussion/discussion.xml',
                 "The tag <discussion url_name='discussion'> does not have the required setting 'discussion_category'.")
    assert_error(errorstore, InvalidSetting, 'discussion/discussion.xml',
                 "The tag <discussion url_name='discussion'> does not have the required setting 'discussion_target'.")
    assert_error(errorstore, Obsolete, 'lti/lti.xml',
                 "The tag <lti url_name='lti'> should be converted to the newer lti_consumer Xblock.")
    assert_error(errorstore, InvalidSetting, 'lti/lti.xml',
                 "The tag <lti url_name='lti'> does not have the required setting 'launch_url'.")
    assert_error(errorstore, LTIError, 'lti/lti.xml',
                 "Course policy does not include an 'lti_passports' entry for 'nothere', required for <lti url_name='lti'>.")
    assert_error(errorstore, LTIError, 'lti/lti.xml',
                 "Course policy does not include the 'lti' advanced module, required for <lti url_name='lti'>.")
    assert_error(errorstore, InvalidSetting, 'vertical/vertical.xml',
                 "The tag <lti_consumer url_name='meep'> does not have the required setting 'launch_url'.")
    assert_error(errorstore, LTIError, 'vertical/vertical.xml',
                 "Course policy does not include an 'lti_passports' entry for 'nothere', required for <lti_consumer url_name='meep'>.")
    assert_error(errorstore, LTIError, 'vertical/vertical.xml',
                 "Course policy does not include the 'lti_consumer' advanced module, required for <lti_consumer url_name='meep'>.")
    assert_error(errorstore, MissingFile, 'course/mycourseurl.xml',
                 "The <course url_name='mycourseurl'> tag contains a reference to a missing static file: course_image_small.jpg")
    assert_error(errorstore, InvalidSetting, 'problem/problem.xml',
                 "The tag <problem url_name='problem'> has a negative problem weight.")
    assert_error(errorstore, InvalidSetting, 'course/mycourseurl.xml',
                 "The tag <course url_name='mycourseurl'> should have a positive number of attempts.")
    assert_error(errorstore, InvalidSetting, 'problem/problem.xml',
                 "The tag <problem url_name='problem'> should have a positive number of attempts.")
    assert_error(errorstore, InvalidSetting, 'vertical/vertical.xml',
                 "The tag <drag-and-drop-v2 url_name='studio_mess2' display_name='This is my title'> has an error in the data JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1).")
    assert_error(errorstore, InvalidSetting, 'vertical/vertical.xml',
                 "The tag <drag-and-drop-v2 url_name='studio_mess3' display_name='This is my title'> data JSON is not a dictionary.")
    assert_error(errorstore, InvalidSetting, 'sequential/examseq.xml',
                 "The tag <sequential url_name='examseq' display_name='Exam'> is a timed exam, but the course policy does not have 'enable_timed_exams=true'.")
    assert_error(errorstore, DateOrdering, 'vertical/oravert.xml',
                 "The tag <openassessment url_name='paper-draft'> has a date out of order: assessment 1 due date must be before course end date")
    assert_caught_all_errors(errorstore)

    # Ensure that we got the scripts from the problem file
    assert set(url_names['problem'].scripts) == {'python', 'perl', 'javascript'}
    # Also make sure we detected the response types
    assert set(url_names['problem'].response_types) == {'customresponse', 'multiplechoiceresponse'}
    # as well as the input types
    assert set(url_names['problem'].input_types) == {'choicegroup', 'textline'}
    # We also found the solution
    assert url_names['problem'].has_solution

    # Make sure our exam sequential was detected
    assert url_names['examseq'].is_exam


def test_validate_course10():
    """This test includes all validation steps. The course is designed to test the validators and slow validators."""
    course, errorstore, url_names = validate("testcourses/testcourse10")
    handle_general_errors_in_10(errorstore)
    handle_display_name_errors_in_10(errorstore)
    handle_discussion_id_errors_in_10(errorstore)
    handle_link_errors_in_10(errorstore)
    assert_caught_all_errors(errorstore)


def test_validate_course11():
    """
    Tests validate when given a set of allowed xblocks.

    The test course uses currently unsupported xblocks which
    could fail the validate call.
    """
    allowed_xblocks = [
        "recommender",
        "edx_sga",
        "crowdsourcehinter",
        "done",
        "word_cloud"
    ]
    total_errors = len(allowed_xblocks)
    validate_kwargs = dict(filename="testcourses/testcourse11", steps=1)
    # recommender, edx_sga, crowdsourcehinter, done, word_cloud
    course, errorstore, url_names = validate(**validate_kwargs)
    assert len(errorstore.errors) == total_errors

    current_allowed_xblocks = []
    for xblock in allowed_xblocks:
        current_allowed_xblocks.append(xblock)
        # Do not throw error when an xblock is allowed.
        course, errorstore, url_names = validate(**validate_kwargs, allowed_xblocks=current_allowed_xblocks)
        assert len(errorstore.errors) == total_errors - len(current_allowed_xblocks)
