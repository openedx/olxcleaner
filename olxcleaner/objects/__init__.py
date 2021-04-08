# -*- coding: utf-8 -*-
"""
objects subpackage

Contains classes to describe various edX objects

Note that each edX object has its own file

Use the EdxCourse.get_object method to create objects of appropriate tags
"""
from olxcleaner.objects.common import EdxObject
from olxcleaner.objects.chapter import EdxChapter
from olxcleaner.objects.course import EdxCourse
from olxcleaner.objects.discussion import EdxDiscussion
from olxcleaner.objects.html import EdxHtml
from olxcleaner.objects.lti import EdxLti
from olxcleaner.objects.lti_consumer import EdxLtiConsumer
from olxcleaner.objects.problem import EdxProblem
from olxcleaner.objects.sequential import EdxSequential
from olxcleaner.objects.vertical import EdxVertical
from olxcleaner.objects.video import EdxVideo
from olxcleaner.objects.draganddropv2 import EdxDragAndDropV2
from olxcleaner.objects.openassessment import EdxORA
from olxcleaner.objects.wiki import Wiki
