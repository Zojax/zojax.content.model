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
from zope import interface
from zope.component import getAdapters
from zope.security.proxy import removeSecurityProxy
from zope.publisher.browser import TestRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zojax.content.type.interfaces import IContent

from interfaces import _, IViewModel


class Vocabulary(SimpleVocabulary):

    def getTerm(self, value):
        try:
            return self.by_value[value]
        except KeyError:
            return self.by_value[self.by_value.keys()[0]]


defaultModel = SimpleTerm(u'__default__', '__default__', _('Default'))
defaultModel.description = _('Default content item view presentation.')


class Models(object):
    """
    >>> from zope import interface, component
    >>> factory = Models()

    >>> list(factory(None))
    []

    >>> from zojax.content.type.item import Item
    >>> from zojax.extensions.interfaces import IExtension

    >>> class Content(Item):
    ...     interface.implements(IContent)
    >>> content = Content()
    >>> content.__name__ = 'portal'
    >>> content.__title__ = 'Portal'

    >>> class Extension(object):
    ...     interface.implements(IExtension)
    >>> extension = Extension()
    >>> extension.context = content
    >>> extension.request = None
    >>> extension.__parent__ = content

    >>> from zojax.content.model.model import ViewModelType
    >>> viewModel = ViewModelType('view', title=u'Simple view')

    >>> component.provideAdapter(
    ...    viewModel, (Content, interface.Interface), IViewModel, name='view')

    >>> class View2(object):
    ...     component.adapts(Content, interface.Interface)
    ...     interface.implements(IViewModel)
    ...     title = u'Simple view 2'
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...     def isAvailable(self):
    ...         return False

    >>> from zojax.content.model.model import ViewModelType
    >>> viewModel2 = ViewModelType('view2', View2, title=u'Simple view2')

    >>> component.provideAdapter(
    ...     viewModel2, (Content, interface.Interface), IViewModel, name='view2')

    >>> voc = factory(extension)

    >>> for term in voc:
    ...     print term.value, term.title
    __default__ Default
    view Simple view

    >>> voc.getTerm('view'), voc.getTerm('view').value
    (<zope.schema.vocabulary.SimpleTerm ...>, u'view')

    for unknown value return first term

    >>> voc.getTerm('view'), voc.getTerm('unknown').value
    (<zope.schema.vocabulary.SimpleTerm ...>, u'__default__')

    """
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        while not IContent.providedBy(context):
            context = getattr(context, '__parent__', None)
            if context is None:
                return SimpleVocabulary(())

        try:
            request = getInteraction().participations[0]
        except:
            request = TestRequest()

        terms = []
        for name, view in getAdapters((context, request), IViewModel):
            view.update()
            if not view.isAvailable():
                continue

            term = SimpleTerm(name, name, view.__title__)
            term.description = view.__description__

            terms.append((view.__title__, term))

        terms.sort()
        return Vocabulary([defaultModel] + [term for t, term in terms])
