# -*- coding: utf-8 -*-
"""
xml.py

Routines to load the XML of an edX course into a structure
"""
import os
from os.path import isfile

from lxml import etree
from lxml.etree import XMLSyntaxError

from olxcleaner.exceptions import ClassDoesNotExist
from olxcleaner.loader.xml_exceptions import (CourseXMLDoesNotExist,
                                              CourseXMLName, DuplicateHTMLName,
                                              EmptyTag, URLNameMismatch,
                                              FileDoesNotExist, InvalidHTML,
                                              InvalidPointer, InvalidXML,
                                              NonFlatFilename, NonFlatURLName,
                                              PossibleHTMLPointer,
                                              PossiblePointer, SelfPointer,
                                              TagMismatch, UnexpectedContent,
                                              UnexpectedTag, PointerAlreadyPointedAt)
from olxcleaner.objects import EdxObject


def load_course(directory, filename, errorstore, allowed_xblocks=None):
    """
    Loads a course, given a filename for the appropriate course.xml file.

    :param directory: Path for course.xml (or equivalent)
    :param filename: Filename for course.xml (or equivalent)
    :param errorstore: ErrorStore object to store errors
    :param allowed_xblocks: List of all allowed xblocks.
    :return: EdxCourse object, or None on failure
    """
    # Ensure the file exists
    fullpath = os.path.join(directory, filename)
    if not isfile(fullpath):
        errorstore.add_error(CourseXMLDoesNotExist(fullpath))
        return

    # Check file name
    if filename != "course.xml":
        errorstore.add_error(CourseXMLName(filename))

    # Obtain the XML for the course.xml file
    try:
        tree = etree.parse(fullpath)
    except XMLSyntaxError as e:
        errorstore.add_error(InvalidXML(filename, error=e.args[0]))
        return

    # Initialize the course object
    course = EdxObject.get_object('course')

    # Load the course!
    read_course(course, tree.getroot(), directory, filename, errorstore, {}, allowed_xblocks=allowed_xblocks)

    # Save the course directory and full path in the course object
    course.savedir(directory, fullpath)

    return course


def read_course(edxobj, node, directory, filename, errorstore, htmlfiles, pointer=False, allowed_xblocks=None):
    """
    Takes in the current EdxObject, the current lxml element, and the
    current filename. Reads from the element into the object, creating
    any children for that object, and recursing into them.

    :param edxobj: The current EdxObject
    :param node: The current lxml element
    :param directory: The course directory
    :param filename: The current filename
    :param errorstore: An ErrorStore object that is collecting errors
    :param htmlfiles: A dictionary of XML filenames (value) that reference a given HTML filename (key)
    :param pointer: True if we've arrived at this node due to a pointer tag
    :param allowed_xblocks: List of all allowed xblocks.
    :return: None
    """
    # Make sure that the node matches the edxobj type
    if edxobj.type != node.tag:
        errorstore.add_error(TagMismatch(filename,
                                         tag1=edxobj.type,
                                         tag2=node.tag))
        edxobj.broken = True
        return

    # Start by copying the attributes from the node into the object
    edxobj.add_attribs(node.attrib)
    # Set the filename for the object
    edxobj.add_filename(filename)

    # Is the tag an empty tag? (contains only attributes and comments)
    nodelen = len(node)
    for child in node:
        if child.tag is etree.Comment:
            # We need to remove comment nodes from the length count
            nodelen -= 1
    empty = False
    if nodelen == 0:
        # Check for text
        if node.text is None or node.text.strip() == '':
            empty = True
            # No text, but make sure that the comment children also have no text!
            for child in node:
                if child.tail and child.tail.strip():
                    empty = False

    # Check for a pointer tag
    node_filename = os.path.splitext(os.path.split(filename)[-1])[0]
    if empty and edxobj.is_pointer(node.attrib):
        if pointer:
            node_pointing_to_itself = node.attrib.get('url_name') == node_filename
            if node_pointing_to_itself:
                # The target of a pointer tag cannot be a pointer itself
                pointer_error = SelfPointer
            else:
                # The target of a pointer has been pointed to and is unexpectedly empty.
                pointer_error = PointerAlreadyPointedAt

            errorstore.add_error(pointer_error(filename, edxobj=edxobj))
            edxobj.broken = True
            return

        # We have a valid pointer tag
        url_name = edxobj.attributes['url_name']
        if ":" in url_name:
            errorstore.add_error(NonFlatURLName(filename, edxobj=edxobj))
            url_name = url_name.replace(":", "/")
        new_file = edxobj.type + "/" + url_name + ".xml"

        # Ensure the file exists
        if not isfile(os.path.join(directory, new_file)):
            errorstore.add_error(FileDoesNotExist(filename,
                                                  edxobj=edxobj,
                                                  new_file=new_file))
            edxobj.broken = True
            return

        try:
            new_node = etree.parse(os.path.join(directory, new_file)).getroot()
        except XMLSyntaxError as e:
            errorstore.add_error(InvalidXML(new_file, error=e.args[0]))
            edxobj.broken = True
            return
        else:
            read_course(edxobj, new_node, directory, new_file, errorstore, htmlfiles, pointer=True,
                        allowed_xblocks=allowed_xblocks)
            return

    # Special case: HTML files can point to an actual HTML file with their 'filename' attribute
    if node.tag == "html" and "filename" in edxobj.attributes:
        new_filename = edxobj.attributes['filename']
        if ":" in new_filename:
            new_filename = new_filename.replace(":", "/")
            new_file = "html/" + new_filename + ".html"
            errorstore.add_error(NonFlatFilename(filename, edxobj=edxobj, newfilename=new_file))
        else:
            new_file = "html/" + new_filename + ".html"

        # If not empty, then it could be a PossibleHTMLPointer error
        if not empty:
            if isfile(os.path.join(directory, new_file)):
                errorstore.add_error(PossibleHTMLPointer(filename,
                                                         edxobj=edxobj,
                                                         new_file=new_file))
        else:
            # We are empty, so this is a good pointer
            # Ensure the file exists
            if not isfile(os.path.join(directory, new_file)):
                errorstore.add_error(FileDoesNotExist(filename,
                                                      edxobj=edxobj,
                                                      new_file=new_file))
                return

            try:
                with open(os.path.join(directory, new_file)) as f:
                    html = f.read()
                parser = etree.HTMLParser(recover=False)
                content = etree.fromstring(html, parser)
            except Exception as e:
                errorstore.add_error(InvalidHTML(new_file, error=e.args[0]))
                edxobj.broken = True
                return
            else:
                if new_filename in htmlfiles:
                    errorstore.add_error(DuplicateHTMLName(filename,
                                                           file2=htmlfiles[new_filename],
                                                           htmlfilename=new_file))
                else:
                    htmlfiles[new_filename] = filename
                edxobj.content = content
                edxobj.html_content = True
                return

    # Next, check if the tag shouldn't be empty, and hence should be a pointer
    # but for some reason was an invalid pointer
    if empty and not edxobj.can_be_empty and "url_name" in node.attrib:
        # Likely to be an invalid pointer tag due to too many attributes
        errorstore.add_error(InvalidPointer(filename, edxobj=edxobj))
        edxobj.broken = True
        return

    # At this stage, we've checked for pointer tags and associated errors

    # The pointer url should match with it's filename
    if pointer and "url_name" in node.attrib and not node.attrib.get('url_name') == node_filename:
        errorstore.add_error(URLNameMismatch(filename, tag=node.tag))

    # Is the tag unexpectedly empty?
    if empty and not edxobj.can_be_empty:
        errorstore.add_error(EmptyTag(filename, edxobj=edxobj))
        return

    # If we get here, we have a non-empty tag

    # Check to see if there is a pointer target file that is not being used
    if not pointer and 'url_name' in edxobj.attributes and edxobj.can_be_pointer:
        new_file = edxobj.type + "/" + edxobj.attributes['url_name'] + ".xml"
        if isfile(os.path.join(directory, new_file)):
            errorstore.add_error(PossiblePointer(filename,
                                                 edxobj=edxobj,
                                                 new_file=new_file))

    if edxobj.content_store:
        # Store content from content tags
        edxobj.content = node  # Can convert to text with etree.tostring(node, pretty_print=True)
    else:
        # Check for content in non-content tag
        if node.text and node.text.strip():
            errorstore.add_error(UnexpectedContent(filename,
                                                   edxobj=edxobj,
                                                   text=node.text))
        else:
            for child in node:
                if child.tail and child.tail.strip():
                    errorstore.add_error(UnexpectedContent(filename,
                                                           edxobj=edxobj,
                                                           text=child.tail))
                    break

        # Recurse into each child
        for child in node:
            child_tag = child.tag
            tag_is_allowed = check_tag_is_allowed(child_tag, edxobj.allowed_children, allowed_xblocks)
            tag_is_comment = child_tag is etree.Comment  # Ignore comments
            if tag_is_comment:
                continue
            elif tag_is_allowed:
                try:
                    newobj = EdxObject.get_object(child_tag)
                    edxobj.add_child(newobj)
                    read_course(newobj, child, directory, filename, errorstore, htmlfiles,
                                allowed_xblocks=allowed_xblocks)
                except ClassDoesNotExist:
                    # Do not do anything if an xblock is allowed but currently
                    # not supported by the library
                    pass
            else:
                errorstore.add_error(
                    UnexpectedTag(filename, tag=child_tag, edxobj=edxobj)
                )


def check_tag_is_allowed(tag, allowed_children, allowed_xblocks):
    """
    Checks if a tag is valid or not.

    :param tag: Tag name of the lxml element
    :param allowed_children: List of children/xblocks allowed by the olxcleaner
    :param allowed_xblocks: List of Xblocks that are allowed but may not be supported by the olxcleaner for validation
    """
    if allowed_xblocks is None:
        return tag in allowed_children
    return tag in allowed_xblocks or tag in allowed_children
