# Error Listing

Each error has a name that can be used in the `-i` flag to ignore it.

## Errors

- `BadEntry`: The policy file contains an entry that is not a dictionary.

- `BadPolicyFormat`: The policy file didn't have the expected structure.

- `BadPolicy`: A policy file was not valid JSON.

- `CourseXMLDoesNotExist`: The supplied `course.xml` file does not exist (or could not be opened).

- `DuplicateID`: A discussion ID is duplicated. This leads to the discussion forums randomly telling students that threads have been deleted.

- `DuplicateURLName`: Two tags have the same `url_name` attribute. This can lead to the wrong content loading, and seriously impedes this program's error analysis.

- `FileDoesNotExist`: The file being pointed to does not exist.

- `GradingPolicyIssue`: A catch-all error for issues in the grading policy.

- `InvalidHTML`: The specified HTML file has a syntax error.

- `InvalidPointer`: This tag appears to be trying to point to another file, but contains unexpected attributes, and is hence not pointing.

- `InvalidSetting`: A setting has been set to an invalid value.

- `InvalidXML`: The specified XML file has a syntax error.

- `LTIError`: There appears to be an error in the way that an LTI component is being invoked.

- `NoRunName`: The course tag has no `url_name`, and hence no run name. This is a required parameter for a course.

- `PolicyNotFound`: A policy file was not found.

- `SelfPointer`: A tag appears to be pointing to itself.

- `TagMismatch`: A file purporting to contain a specific tag type (e.g., `problem` or `chapter`) instead contains a different tag.

- `UnexpectedContent`: A tag contains unexpected text content.

- `UnexpectedTag`: A tag was found in an inappropriate location (e.g., a `vertical` in a `chapter`), or the tag was not recognized.

- `WrongObjectType`: The policy file references an object of one type, but that object is found in the course with another type.

## Warnings

- `BadCourseLink`: An internal /course/ link points to a location that doesn't exist.

- `BadJumpToLink`: An internal jump_to_id link points to a url_name that doesn't exist.

- `CourseXMLName`: The master file was not called `course.xml`.

- `DateOrdering`: A date setting appears out of order with another date setting.

- `EmptyTag`: A tag was unexpectedly empty (e.g., a `chapter` tag had no children).

- `ExtraDisplayName`: A tag has a `display_name` attribute when it shouldn't.

- `ExtraURLName`: A tag that had been pointed to by `url_name` from another file has a `url_name` of its own.

- `MissingDisplayName`: A tag is missing the `display_name` attribute. edX will fill a generic name for you.

- `MissingFile`: A file appears to be missing from the static directory.

- `MissingURLName`: A tag is missing the `url_name` attribute. edX will provide a garbage 32-character name for you, but everything is cleaner if you provide a nice name yourself.

- `NonFlatFilename`: A filename pointer for an HTML file uses colon notation to point to a subdirectory. While partially supported, this is not recommended.

- `NonFlatURLName`: A `url_name` pointer uses colon notation to point to a subdirectory. While partially supported, this is not recommended.

- `PolicyRefNotFound`: The policy file references an object that doesn't exist.

- `PossibleHTMLPointer`: This HTML tag looks like it isn't a pointer tag, but a file exists that it could be trying to point to.

- `PossiblePointer`: This tag looks like it isn't a pointer tag, but a file exists that it could be trying to point to. (This file is thus orphaned, as no other tag can point to it due to `url_name` clashes.)

- `SettingOverride`: The policy file is overriding a setting specified in a file.

## Information

- `DuplicateHTMLName`: Two HTML tags point to the same HTML file (`filename` attribute). While this isn't obviously problematic, probably best not to do it.

- `Obsolete`: The way this object has been set up is obsolete.

## Debug

(Currently no errors in this category)
