# -*- coding: utf-8 -*-
"""
slowvalidators.py

Validation routines that act on the course as a whole,
but may require significant time to carry out
"""
from olxcleaner.objects import EdxDragAndDropV2, EdxVertical
from olxcleaner.parser.validators import GlobalValidator
from olxcleaner.utils import traverse, find_links, check_static_file_exists
from olxcleaner.parser.parser_exceptions import BadJumpToLink, BadCourseLink, MissingFile

class SlowValidator(GlobalValidator):
    """Abstract base class for time-consuming validators"""

class CheckLinks(SlowValidator):
    """Searches the course for broken internal links (including static links)"""

    def __call__(self, course, errorstore, url_names):
        for edxobj in traverse(course):
            if edxobj.content_store:
                # Find all of the special links in the object
                links = find_links(edxobj)
                # Make sure that each link has an endpoint!
                validate_links(course, url_names, links, edxobj, errorstore)
            elif isinstance(edxobj, EdxDragAndDropV2):
                # Look inside the data structure of dndv2 objects
                data = edxobj.parsed_data
                links = []
                if 'targetImg' in data:
                    links.append(data['targetImg'])
                if 'items' in data:
                    for entry in data['items']:
                        if 'imageURL' in entry:
                            links.append(entry['imageURL'])
                # Make sure that each link has an endpoint!
                validate_links(course, url_names, links, edxobj, errorstore)

def validate_links(course, url_names, links, edxobj, errorstore):
    """Takes in the links for an edxobj, and processes all links"""
    for link in links:
        if link.startswith('/jump_to_id/'):
            url_name = link[len('/jump_to_id/'):]
            if url_name not in url_names:
                errorstore.add_error(BadJumpToLink(edxobj.filenames[-1], edxobj=edxobj, link=link))

        elif link.startswith('/course/'):
            # Call a routine to handle this one
            follow_course_link(course, link, edxobj, errorstore)

        elif link.startswith('/static/'):
            # Call a routine to handle this one
            follow_static_link(course, link, edxobj, errorstore)

def follow_course_link(course, link, edxobj, errorstore):
    """
    Follow a course link, reporting an error if it's invalid.

    :param course: Course object
    :param link: Link to chase
    :param edxobj: Object with the link (for reporting purposes)
    :param errorstore: ErrorStore object (for reporting purposes)
    :return: None
    """
    # We need to split the link into pieces
    link_parts = link[len('/course/'):].split("/")

    if link_parts[0] == 'pdfbook':
        # If this is a textbook link, then we're not presently equipped to follow it
        # TODO: Check for links to textbooks
        return
    elif link_parts[0] != 'courseware':
        # Anything other than courseware can't be linked to either
        # e.g., Discussion forum links can never be checked...
        # TODO: Check for links to tabs (which can in principle be checked...)
        return

    # We now try to follow the path
    idx = 1
    current_obj = course
    last_term = False

    while True:
        # If we're out of link parts, we've followed the link as far as it requires
        if idx == len(link_parts) or last_term:
            return

        # If there's a ? in the link part, must be the last term
        # We ignore the ? instruction
        if "?" in link_parts[idx]:
            link_parts[idx] = link_parts[idx].split("?")[0]
            last_term = True

        # If the currently entry is empty, also good (must be done after checking for ?)
        if link_parts[idx] == "":
            return

        # If the current_obj is a vertical, then the next link part must be interpreted as an index
        if isinstance(current_obj, EdxVertical):
            try:
                link_idx = int(link_parts[idx])
            except ValueError:
                # Can't convert the entry to an index; link is bad
                errorstore.add_error(BadCourseLink(edxobj.filenames[-1], edxobj=edxobj, link=link))
                return

            if link_idx < 1 or link_idx > len(current_obj.children):
                # Link doesn't seem to point to somewhere that exists; link is bad
                errorstore.add_error(BadCourseLink(edxobj.filenames[-1], edxobj=edxobj, link=link))

            # Regardless of what happened, we're now done
            return
        else:
            # Scan the current object's children to look for the desired link
            for child in current_obj.children:
                if child.attributes.get('url_name') == link_parts[idx]:
                    # Follow it
                    current_obj = child
                    idx += 1
                    # Continue in the while loop
                    break
            else:
                # Didn't find something to follow, link is bad
                errorstore.add_error(BadCourseLink(edxobj.filenames[-1], edxobj=edxobj, link=link))
                return

def follow_static_link(course, link, edxobj, errorstore):
    """
    Check to see if a static file exists, reporting an error if it's invalid.

    :param course: Course object
    :param link: Link to chase
    :param edxobj: Object with the link (for reporting purposes)
    :param errorstore: ErrorStore object (for reporting purposes)
    :return: None
    """
    file_name = link[len('/static/'):]
    if not check_static_file_exists(course, file_name):
        errorstore.add_error(MissingFile(edxobj.filenames[-1],
                                         edxobj=edxobj,
                                         missing_file=link))
