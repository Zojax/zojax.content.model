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
from zope.schema import getFieldNames
from zope.component import getMultiAdapter
from zojax.layout.interfaces import IPagelet
from zojax.layoutform import Fields, PageletEditForm
from zojax.content.model.interfaces import IModelEdit, IViewModelExtension


class ViewModelExtension(PageletEditForm):

    viewModel = None
    fields = Fields(IViewModelExtension)

    def update(self):
        super(ViewModelExtension, self).update()

        if self.context.view != '__default__':
            viewModel = self.context.getViewModel()
            if viewModel is not None:
                self.viewModel = getMultiAdapter(
                    (viewModel, self.request), IModelEdit)
                self.viewModel.update()


class ViewModelEditForm(PageletEditForm):

    allow = False
    prefix = 'viewmodeledit.'

    @property
    def fields(self):
        return Fields(self.context.__schema__)

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    def update(self):
        if self.context.__schema__ and getFieldNames(self.context.__schema__):
            self.allow = True
            super(ViewModelEditForm, self).update()

    def render(self):
        if self.allow:
            return super(ViewModelEditForm, self).render()
        else:
            return u''
