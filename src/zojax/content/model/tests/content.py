##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import interface, schema
from zojax.content.type.item import Item
from zojax.content.type.container import ContentContainer
from zojax.content.type.interfaces import IItem, IContentContainer


class IMyContent(IItem):
    """ """

class IMyContentContainer(IItem, IContentContainer):
    """ """


class MyContent(Item):
    interface.implements(IMyContent)


class MyContentView(object):

    def render(self):
        return '\n<div>My Content Body: %s</div>\n'%self.context.title


class MyContentContainer(ContentContainer):
    interface.implements(IMyContentContainer)
