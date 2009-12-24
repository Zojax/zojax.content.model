======================
View 'Model' extension
======================

  >>> from zope import component, interface
  >>> from zope.publisher.browser import TestRequest
  >>> from zojax.extensions.interfaces import extensionMarker
  >>> from zojax.content.type.item import Item
  >>> from zojax.content.type.interfaces import IContent
  >>> from zojax.content.model import interfaces
  >>> from zojax.content.model.model import ViewModel, ViewModelType

We need content object

  
  >>> class IMyContent(interface.Interface):
  ...     pass
  
  >>> class MyContent(Item):
  ...     interface.implements(IMyContent, IContent)

  >>> content = MyContent('Test content')

Now we should define default view for content

  >>> from zope.publisher.browser import BrowserPage
  >>> class View(BrowserPage):
  ...     component.adapts(IMyContent, interface.Interface)
  ...     def __call__(self):
  ...         return u'Default view'

  >>> component.provideAdapter(View, provides=interface.Interface, name='index.html')

Render default view

  >>> request = TestRequest()
  >>> component.getMultiAdapter((content, request), name='index.html')()
  u'Default view'

Dynamic view extension

  >>> from zojax.content.model import interfaces
  >>> extension = component.getMultiAdapter(
  ...     (content, request, extensionMarker), interfaces.IViewModelExtension)

it's not avaiulable because there is no registered dynamic views

  >>> extension.isAvailable()
  False


Let's define dynamic view

  >>> class MyModelView(ViewModel):
  ...     component.adapts(IMyContent, interface.Interface)
  ...     interface.implements(interfaces.IViewModel, interfaces.IModelRenderer)
  ...     
  ...     __name__ = u'mymodelview'
  ...     __title__ = u'My model view'
  ...     __description__ = u''
  ...     __schema__ = None
  ...     
  ...     def render(self):
  ...         return 'My Model View: %s'%self.context.title
  ...         
  ...     def __call__(self):
  ...        return self.render()

  >>> component.provideAdapter(
  ...     MyModelView, (IMyContent, interface.Interface),
  ...     interfaces.IViewModel, name='mymodelview')


Changing default view with extention

  >>> extension = component.getMultiAdapter(
  ...     (content, request, extensionMarker), interfaces.IViewModelExtension)
  >>> extension.enabled
  False
  >>> extension.view = 'mymodelview'
  >>> extension.enabled = True

  >>> component.getMultiAdapter((content, request), name='index.html')()
  u'My Model View: Test content'

  >>> extension.enabled = False


zojax:viewmodel directive
=========================

Load directive declaration

  >>> from zojax.content import model
  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.file('meta.zcml', model)

Let's define model

  >>> class MyModelView2(object):
  ...     interface.implements(interfaces.IModelRenderer)
  ...     
  ...     def render(self):
  ...         return 'My Model View 2: %s'%self.context.title
  ...         
  ...     def __call__(self):
  ...        return self.render()

  >>> context = xmlconfig.string("""
  ... <configure xmlns:zojax="http://namespaces.zope.org/zojax" i18n_domain="zojax">
  ...   <zojax:viewmodel
  ...     name="mymodelview2"
  ...     title="My model view 2"
  ...     for="zojax.content.model.README.IMyContent"
  ...     class="zojax.content.model.README.MyModelView2" />
  ... </configure>""", context)

  >>> model = component.getMultiAdapter(
  ...     (content, request), interfaces.IViewModel, 'mymodelview2')
  >>> model.__id__
  u'mymodelview2'
  
  >>> model.__title__
  u'My model view 2'
  
  >>> isinstance(model, MyModelView2)
  True

  >>> extension = component.getMultiAdapter(
  ...     (content, request, extensionMarker), interfaces.IViewModelExtension)
  >>> extension.enabled
  False
  >>> extension.view = 'mymodelview2'
  >>> extension.enabled = True

  >>> component.getMultiAdapter((content, request), name='index.html')()
  u'My Model View 2: Test content'

  >>> extension.enabled = False
