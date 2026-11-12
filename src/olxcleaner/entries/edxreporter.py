# -*- coding: utf-8 -*-
"""
edxreporter.py

This script crawls through a course and produces a LaTeX document
containing the course structure. If vertical names have a timestamp of
the form "(mm:ss)" in them, the total duration of videos for the
sequential will be calculated.

Recommended usage:
edxreporter > report.tex

If you get this error:
Character cannot be encoded into LaTeX: U+FEFF - `'
then you have some bad unicode in your display_name entries: Look through
the LaTeX file for {\bfseries ?}, which is what that character is converted
into.
"""
import sys
import argparse
import datetime
import re
from pylatexenc.latexencode import utf8tolatex

from olxcleaner import validate

def handle_arguments():
    """Look after all command-line arguments"""
    parser = argparse.ArgumentParser(description="edX XML Reporter")

    # Required arguments
    # Location of course.xml
    parser.add_argument("-c", "--course", help="Location of course.xml (default=./course.xml)", default="course.xml")

    # Optional arguments
    # Include url_names with verticals
    parser.add_argument("-u", "--url_names", help="Include url_names with verticals", action="store_true")

    # Parse the command line
    return parser.parse_args()

def sanitize(text):
    """
    This is a helper function that should be used to sanitize text for LaTeX output.
    You'll probably need to edit the LaTeX slightly afterwards, but it should look pretty good!
    """
    results = text
    # Fix quotation marks
    if results.startswith('"'):
        results = "``" + results[1:]
    if results.startswith("'"):
        results = "`" + results[1:]
    results = results.replace(" '", ' `')
    results = results.replace(' "', ' ``')
    results = results.replace('"', "''")
    # Fix unicode characters. Bad characters are replaced by a bold '?'
    results = utf8tolatex(results, substitute_bad_chars=True)
    # Fix math entries a^b
    results = re.sub(r'(.\^.)', r'$\1$', results)
    # Fix math entries a_b (note that utf8tolatex has converted _ to {\_})
    results = re.sub(r'(.){\\_}(.)', r'$\1_\2$', results)
    return results

# Here's the header of the LaTeX file we'll produce
header = r"""\documentclass{article}

\usepackage[english]{babel}
\usepackage{helvet}
\usepackage{microtype}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage[landscape,twocolumn]{geometry}
\usepackage{fullpage}

\special{papersize=8.5in,11in}
\setlength{\pdfpageheight}{\paperheight}
\setlength{\pdfpagewidth}{\paperwidth}
\setlength{\columnsep}{20pt}
\righthyphenmin2
\sloppy

\parskip = 1mm

\titleformat*{\section}{\large\bfseries\raggedright}
\setlist{topsep=0pt}

\begin{document}

\title{[coursetitlehere]}

\date{}

\maketitle

\vspace{-1.5cm}

Each page represents one chapter of material.

"""

# And here's the footer
footer = r"""
\end{document}"""


def main():
    """Entry point for command line instantiation"""
    # Read the command line arguments
    args = handle_arguments()

    # Load the course
    # We need XML structure + policy information, so go to step 4
    course, _, _ = validate(args.course, steps=4)

    # Make sure we have a course to crawl
    if not course:
        print("Cannot load course - aborting")
        sys.exit(1)

    # Crawl the course extracting the desired information
    chapters = []
    for chapter in course.children:
        name = chapter.attributes.get('display_name', '(Unnamed)')
        chapter_log = {'title': sanitize(name), 'sequentials': []}

        for seq in chapter.children:
            name = seq.attributes.get('display_name', '(Unnamed)')
            seq_log = {'title': sanitize(name), 'verticals': []}

            # Total up the duration of all videos in the sequential
            duration = datetime.timedelta()
            for vert in seq.children:
                name = vert.attributes.get('display_name', '(Unnamed)')
                if args.url_names:
                    url_name = vert.attributes.get('url_name', '(no url_name)')
                    seq_log['verticals'].append(f"({url_name}) {sanitize(name)}")
                else:
                    seq_log['verticals'].append(sanitize(name))

                for entry in vert.children:
                    if entry.type == "video":
                        # Search for a duration in the display_name of the form "(mins:seconds)"
                        name = entry.attributes.get('display_name', '')
                        length = re.search(r'\(([0-9]+):([0-9]+)\)', name)
                        if length:
                            minutes = int(length.group(1))
                            seconds = int(length.group(2))
                            duration += datetime.timedelta(minutes=minutes, seconds=seconds)

            if duration.total_seconds() > 0:
                # Report the total time
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                hours = int(hours)
                minutes = int(minutes)
                seconds = int(seconds)
                if hours == 0:
                    seq_log['title'] += f" ({minutes}:{seconds:02})"
                else:
                    seq_log['title'] += f" ({hours}:{minutes:02}:{seconds:02})"

            chapter_log['sequentials'].append(seq_log)
        chapters.append(chapter_log)

    # Now do the output
    coursetitle = course.attributes.get('display_name', 'Unnamed Course')
    coursetitle += r" \\ Overview of Course Content"
    print(header.replace('[coursetitlehere]', coursetitle))

    # Iterate over the content
    needsnewpage = False
    for chapter in chapters:

        # Each chapter should be on its own page
        if needsnewpage:
            print("\n" + r"\newpage" + "\n")

        print(r"\section*{" + chapter['title'] + "}")

        for sequential in chapter['sequentials']:
            print("\n" + r"\section*{" + sequential['title'] + "}\n")
            print(r"\begin{itemize}")

            for vertical in sequential['verticals']:
                print(r"\item " + vertical)

            print(r"\end{itemize}")

        needsnewpage = True

    print(footer)
