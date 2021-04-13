"""
test_validators.py

Tests for validators and slow validators
"""
from olxcleaner import validate
from olxcleaner.loader.xml_exceptions import TagMismatch
from olxcleaner.parser.validators import CheckDisplayNames, CheckDiscussionIDs
from olxcleaner.parser.slowvalidators import CheckLinks
from tests.helpers import assert_caught_all_errors, assert_error
from olxcleaner.parser.parser_exceptions import (MissingDisplayName, ExtraDisplayName, Obsolete,
                                                 DuplicateID, BadJumpToLink, MissingFile, BadCourseLink)
from olxcleaner.utils import find_links

def test_display_names():
    # Perform all steps on course 10 up to validation steps
    course, errorstore, url_names = validate("testcourses/testcourse10", 6)
    handle_general_errors_in_10(errorstore)
    assert_caught_all_errors(errorstore)

    # Check the display names
    validator = CheckDisplayNames()
    validator(course, errorstore, url_names)

    # Catch everything!
    handle_display_name_errors_in_10(errorstore)
    assert_caught_all_errors(errorstore)

def handle_general_errors_in_10(errorstore):
    assert_error(errorstore, TagMismatch, 'chapter/broken_chapter.xml', "The file is of type <chapter> but opens with a <sequential> tag")
    assert_error(errorstore, Obsolete, 'vertical/dndvert.xml', "The tag <lti url_name='lti2' display_name='something'> should be converted to the newer lti_consumer Xblock.")
    assert_error(errorstore, TagMismatch, 'html/tagmismatch.xml', "The file is of type <html> but opens with a <div> tag")


def handle_display_name_errors_in_10(errorstore):
    assert_error(errorstore, MissingDisplayName, 'course/mycourseurl.xml', "The tag <course url_name='mycourseurl'> is missing the display_name attribute.")
    assert_error(errorstore, MissingDisplayName, 'course/mycourseurl.xml', "The tag <html url_name='html'> is missing the display_name attribute.")
    assert_error(errorstore, ExtraDisplayName, 'vertical/oravert.xml', "The tag <openassessment url_name='paper-draft' display_name='Hah!'> has an erroneous display_name attribute.")

def test_discussion_ids():
    # Perform all steps on course 10 up to validation steps
    course, errorstore, url_names = validate("testcourses/testcourse10", 6)
    handle_general_errors_in_10(errorstore)
    assert_caught_all_errors(errorstore)

    # Check the discussion IDs
    validator = CheckDiscussionIDs()
    validator(course, errorstore, url_names)

    # Catch everything!
    handle_discussion_id_errors_in_10(errorstore)
    assert_caught_all_errors(errorstore)

def handle_discussion_id_errors_in_10(errorstore):
    assert_error(errorstore, DuplicateID, 'course/mycourseurl.xml', "The <discussion display_name='Here's a discussion'> tag and the <discussion display_name='Here's a discussion'> tag both use the same discussion id: Me")

def test_link_checking():
    """Checks for broken internal links"""
    # Perform all steps on course 10 up to validation steps
    course, errorstore, url_names = validate("testcourses/testcourse10", 6)
    handle_general_errors_in_10(errorstore)
    assert_caught_all_errors(errorstore)

    # Check the link-finding routines
    links = find_links(url_names['linktest'])
    assert set(links) == {'/course/courseware/testing',
                          '/course/courseware/broken_chapter',
                          '/course/courseware/chapter/sequential',
                          '/course/courseware/chapter/sequential/',
                          '/course/courseware/chapter/sequential/vertical',
                          '/course/courseware/chapter/sequential/vertical/',
                          '/course/courseware/chapter/sequential/vertical/1',
                          '/course/courseware/chapter/sequential/vertical/10',
                          '/course/courseware/chapter/sequential/vertical/0',
                          '/course/courseware/chapter/sequential/vertical/html',
                          '/course/courseware/chapter/sequential/vertical/1?last_child',
                          '/course/courseware/chapter/sequential/vertical/?last_child',
                          '/course/courseware/chapter/sequential/vertical?last_child',
                          '/static/testing.png',
                          '/static/testing2.css',
                          '/jump_to_id/oravert',
                          '/jump_to_id/oravert2',
                          '/static/image.png',
                          '/course/discussion/somewhere',
                          '/course/pdfbook/0/chapter/9/11'}

    # Check the links
    validator = CheckLinks()
    validator(course, errorstore, url_names)

    # Catch everything!
    handle_link_errors_in_10(errorstore)
    assert_caught_all_errors(errorstore)

def handle_link_errors_in_10(errorstore):
    assert_error(errorstore, BadJumpToLink, 'html/linktest.xml', "The <html url_name='linktest' display_name='Testing links'> tag contains a link to a url_name that doesn't exist: /jump_to_id/oravert2")
    assert_error(errorstore, MissingFile, 'html/linktest.xml', "The <html url_name='linktest' display_name='Testing links'> tag contains a reference to a missing static file: /static/testing2.css")
    assert_error(errorstore, MissingFile, 'html/linktest.xml', "The <html url_name='linktest' display_name='Testing links'> tag contains a reference to a missing static file: /static/testing.png")
    assert_error(errorstore, BadCourseLink, 'html/linktest.xml', "The <html url_name='linktest' display_name='Testing links'> tag contains a link to a location that doesn't exist: /course/courseware/testing")
    assert_error(errorstore, BadCourseLink, 'html/linktest.xml', "The <html url_name='linktest' display_name='Testing links'> tag contains a link to a location that doesn't exist: /course/courseware/chapter/sequential/vertical/10")
    assert_error(errorstore, BadCourseLink, 'html/linktest.xml', "The <html url_name='linktest' display_name='Testing links'> tag contains a link to a location that doesn't exist: /course/courseware/chapter/sequential/vertical/0")
    assert_error(errorstore, BadCourseLink, 'html/linktest.xml', "The <html url_name='linktest' display_name='Testing links'> tag contains a link to a location that doesn't exist: /course/courseware/chapter/sequential/vertical/html")
    assert_error(errorstore, MissingFile, 'vertical/dndvert.xml', "The <problem url_name='dndtest' display_name='Mwa'> tag contains a reference to a missing static file: /static/ex34_dnd_sol.png")
    assert_error(errorstore, MissingFile, 'vertical/dndvert.xml', "The <problem url_name='dndtest' display_name='Mwa'> tag contains a reference to a missing static file: /static/ex34_dnd.png")
    assert_error(errorstore, MissingFile, 'vertical/dndvert.xml', "The <problem url_name='dndtest' display_name='Mwa'> tag contains a reference to a missing static file: /static/ex34_dnd_label1.png")
    assert_error(errorstore, MissingFile, 'vertical/dnd2vert.xml', "The <drag-and-drop-v2 url_name='studio_mess' display_name='This is my title'> tag contains a reference to a missing static file: /static/ex34_dnd.png")
    assert_error(errorstore, MissingFile, 'vertical/dnd2vert.xml', "The <drag-and-drop-v2 url_name='studio_mess' display_name='This is my title'> tag contains a reference to a missing static file: /static/ex34_dnd_label1.png")
