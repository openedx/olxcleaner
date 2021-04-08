"""
test_load_xml.py

Tests for XML course loading
"""
from lxml import etree
from tests.helpers import assert_error, assert_caught_all_errors

from olxcleaner.loader.xml import load_course
from olxcleaner.errorstore import ErrorStore
from olxcleaner.loader.xml_exceptions import (
    CourseXMLDoesNotExist,
    InvalidXML,
    CourseXMLName,
    TagMismatch,
    SelfPointer,
    FileDoesNotExist,
    NonFlatURLName,
    NonFlatFilename,
    InvalidPointer,
    UnexpectedTag,
    InvalidHTML,
    ExtraURLName,
    UnexpectedContent,
    EmptyTag,
    PossiblePointer,
    PossibleHTMLPointer,
    DuplicateHTMLName
)

def test_no_course():
    errorstore = ErrorStore()
    course = load_course("testcourses", "nocourse.xml", errorstore)
    handle_nocourse_errors(errorstore)
    assert_caught_all_errors(errorstore)

def handle_nocourse_errors(errorstore):
    assert_error(errorstore, CourseXMLDoesNotExist, 'testcourses/nocourse.xml', 'The file \'testcourses/nocourse.xml\' does not exist.')

def test_course1():
    """Make sure that things load properly when everything is ok"""
    errorstore = ErrorStore()
    course = load_course("testcourses/testcourse1", "course.xml", errorstore)
    assert errorstore.errors == []

    assert course.attributes == {'url_name': 'mycourseurl', 'org': 'myorg', 'course': 'mycourse'}

    [chapter] = course.children
    assert chapter.attributes == {'url_name': 'chapter', 'display_name': 'chapter name'}

    [sequential] = chapter.children
    assert sequential.attributes == {'url_name': 'sequential', 'display_name': 'display name'}

    [vertical] = sequential.children
    assert vertical.attributes == {'url_name': 'vertical', 'display_name': 'vertical name'}

    [html] = vertical.children
    assert html.attributes == {'url_name': 'html', 'display_name': 'html name'}
    assert '<p>Test course</p>' in etree.tostring(html.content, pretty_print=True).decode()

def test_course2():
    """Test for XML loading errors"""
    errorstore = ErrorStore()
    course = load_course("testcourses/testcourse2", "coursefile.xml", errorstore)
    handle_course2_errors(errorstore)
    assert_caught_all_errors(errorstore)

def handle_course2_errors(errorstore):
    assert_error(errorstore, CourseXMLName, 'coursefile.xml', 'The course file, coursefile.xml, is not named course.xml')
    assert_error(errorstore, ExtraURLName, 'sequential/mysequential.xml', "The opening <sequential> tag shouldn't have a url_name attribute")
    assert_error(errorstore, FileDoesNotExist, 'sequential/mysequential.xml', "The <vertical url_name='myverticalnone'> tag points to the file vertical/myverticalnone.xml that does not exist")
    assert_error(errorstore, EmptyTag, 'vertical/myvertical4.xml', "The <vertical url_name='myvertical4' display_name='Hello'> tag is unexpectedly empty")
    assert_error(errorstore, EmptyTag, 'sequential/mysequential.xml', "The <vertical> tag is unexpectedly empty")
    assert_error(errorstore, UnexpectedContent, 'vertical/myvertical4-2.xml', "The <vertical url_name='myvertical4-2' display_name='Hello'> tag should not contain any text (but not really...)")
    assert_error(errorstore, InvalidXML, 'vertical/myvertical5.xml', 'Opening and ending tag mismatch: vertical line 1 and chapter, line 2, column 11')
    assert_error(errorstore, UnexpectedTag, 'vertical/myvertical6.xml', "A <vertical> tag was unexpectedly found inside the <vertical url_name='myvertical6' display_name='Hello'> tag")
    assert_error(errorstore, UnexpectedTag, 'sequential/mysequential.xml', "A <chapter> tag was unexpectedly found inside the <vertical> tag")
    assert_error(errorstore, TagMismatch, 'vertical/myvertical7.xml', 'The file is of type <vertical> but opens with a <chapter> tag')
    assert_error(errorstore, SelfPointer, 'vertical/myvertical8.xml', "The tag <vertical url_name='myvertical8'> tag appears to be pointing to itself")
    assert_error(errorstore, InvalidPointer, 'sequential/mysequential.xml', "The <vertical url_name='myvertical9' display_name='Hi there'> tag looks like it is an invalid pointer tag")
    assert_error(errorstore, UnexpectedContent, 'vertical/myvertical10.xml', "The <vertical url_name='myvertical10' display_name='something'> tag should not contain any text (Here is some co...)")
    assert_error(errorstore, UnexpectedContent, 'sequential/mysequential.xml', "The <vertical> tag should not contain any text (Here's some bad...)")
    assert_error(errorstore, InvalidHTML, 'html/html3.html', 'InvalidHTML (html/html3.html): Unexpected end tag : b, line 1, column 34')
    assert_error(errorstore, PossiblePointer, 'vertical/myvertical1.xml', "The <problem url_name='problem2'> tag is not a pointer, but a file that it could point to exists (problem/problem2.xml)")
    assert_error(errorstore, PossibleHTMLPointer, 'html/html6.xml', "The <html url_name='html6'> tag is not a pointer, but a file that it could point to exists (html/html3.html)")
    assert_error(errorstore, PossibleHTMLPointer, 'vertical/myvertical3.xml', "The <html> tag is not a pointer, but a file that it could point to exists (html/html3.html)")
    assert_error(errorstore, NonFlatURLName, 'vertical/myvertical2.xml', "The <video url_name='stuff:video2'> tag uses obsolete colon notation in the url_name to point to a subdirectory")
    assert_error(errorstore, NonFlatFilename, 'html/html2.xml', "The <html url_name='html2'> tag uses obsolete colon notation to point to a subdirectory for filename html/stuff/html2.html")
    assert_error(errorstore, NonFlatFilename, 'vertical/myvertical3.xml', "The <html> tag uses obsolete colon notation to point to a subdirectory for filename html/stuff/here.html")
    assert_error(errorstore, FileDoesNotExist, 'html/html4.xml', "The <html url_name='html4'> tag points to the file html/htmlnotexist.html that does not exist")
    assert_error(errorstore, FileDoesNotExist, 'vertical/myvertical3.xml', "The <html> tag points to the file html/nonexistant.html that does not exist")
    assert_error(errorstore, DuplicateHTMLName, 'vertical/myvertical3.xml', "Two html tags refer to the same HTML file (using the 'filename' attribute): html/html7.html is referenced in vertical/myvertical3.xml and html/html7.xml")
    assert_error(errorstore, EmptyTag,'problem/problem3.xml' , "The <problem url_name='problem3' display_name='Blank Common Problem'> tag is unexpectedly empty")

def test_course3():
    """Test for XML error in course.xml"""
    errorstore = ErrorStore()
    course = load_course("testcourses/testcourse3", "course.xml", errorstore)
    assert_error(errorstore, InvalidXML, 'course.xml', 'attributes construct error, line 1, column 61')
    assert_caught_all_errors(errorstore)
