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
""" zojax content marker tests

$Id$
"""
import os.path
import unittest, doctest
from zope import interface, component
from zope.schema.vocabulary import getVocabularyRegistry
from zope.app.testing import setup, functional
from zope.app.component import hooks
from zope.app.rotterdam import Rotterdam
from zope.dublincore.testing import setUpDublinCore
from zope.annotation.attribute import AttributeAnnotations
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.testing.functional import ZCMLLayer, FunctionalDocFileSuite

from zojax.extensions import storage
from zojax.extensions.zcml import Wrapper
from zojax.extensions.interfaces import ExtensionMarker
from zojax.extensions.extensiontype import ExtensionType
from zojax.content.model.vocabulary import Models
from zojax.content.model.extension import ViewModelExtension
from zojax.content.model.interfaces import IViewModelSupport
from zojax.content.model.interfaces import IViewModelExtension
from zojax.content.model.browser.renderer import ViewModelRenderer
from zojax.layout.pagelet import BrowserPagelet
from zojax.layoutform.interfaces import ILayoutFormLayer
from zojax.content.model.tests import content

class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """

zojaxContentModelLayout = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxContentModelLayout', allow_teardown=True)


class Renderer(ViewModelRenderer, BrowserPagelet):

    index = ViewPageTemplateFile(
        os.path.join(os.path.dirname(__file__), '..', 'browser', 'renderer.pt'))


def setUp(test):
    setup.placefulSetUp(True)
    setUpDublinCore()
    component.provideAdapter(storage.Storage)
    component.provideAdapter(AttributeAnnotations)

    hooks.setHooks()
    setup.setUpTraversal()
    setup.setUpSiteManagerLookup()
    setup.setUpTestAsModule(test, 'zojax.content.model.README')

    # generate extension
    ExtensionClass = ExtensionType(
        "content.model",
        IViewModelExtension, ViewModelExtension,
        "View Model", "View model extension.", layer=interface.Interface)

    # register adater
    component.provideAdapter(
        Wrapper(ExtensionClass),
        (interface.Interface, interface.Interface, ExtensionMarker),
        IViewModelExtension)

    # register vocabulary
    getVocabularyRegistry().register(
        'zojax.content.model-list', Models())

    component.provideAdapter(
        Renderer, (IViewModelSupport, interface.Interface),
        interface.Interface, name='index.html')


def FunctionalModelDocFileSuite(*paths, **kw):
    globs = kw.setdefault('globs', {})
    globs['getRootFolder'] = functional.getRootFolder

    kwsetUp = kw.get('setUp')
    def setUp(test):
        root = functional.getRootFolder()
        if 'content' not in root:
            root['content'] = content.MyContent(u'My Content')

        if 'container' not in root:
            root['container'] = content.MyContentContainer(u'My Content Container')
            root['container']['content1'] = content.MyContent(u'My Content 1')
            root['container']['content2'] = content.MyContent(u'My Content 2')
            root['container']['content3'] = content.MyContent(u'My Content 3')

    kw['setUp'] = setUp
    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = kw.get('layer', zojaxContentModelLayout)
    return suite

def test_suite():
    return unittest.TestSuite((
        FunctionalModelDocFileSuite("testbrowser.txt"),
        doctest.DocFileSuite(
            '../README.txt',
            setUp=setUp,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocTestSuite(
            'zojax.content.model.model',
            setUp=setUp,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocTestSuite(
            'zojax.content.model.vocabulary',
            setUp=setUp,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
