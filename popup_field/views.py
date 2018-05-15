from django.utils.decorators import classonlymethod
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import JsonResponse
from django.template.response import TemplateResponse
from django.core.exceptions import ImproperlyConfigured
from django.urls import path, include

from .fields import ForeignKeyWidget, ManyToManyWidget


class AttributeThunk(object):
    """
    Class thunks various attributes expected by Django generic CRUD views as
    properties of the parent viewset class instance. This allows us to
    normalize all CRUD view attributes as ViewSet properties and/or methods.
    """

    def __init__(self, viewset, *args, **kwargs):
        self._viewset = viewset()
        self.raise_exception = self._viewset.raise_exception
        # allow viewset methods to access view
        self._viewset.view = self
        # self._viewset.template_name_create = self._viewset.template_name_create
        # self._viewset.template_name_update = self._viewset.template_name_update
        super(AttributeThunk, self).__init__(*args, **kwargs)

    @property
    def model(self):
        return self._viewset.model

    @property
    def fields(self):
        return self._viewset.fields

    def get_form_class(self):
        if hasattr(self._viewset, 'form_class'):
            return self._viewset.form_class
        return super(AttributeThunk, self).get_form_class()

    def get_form_kwargs(self):
        kwargs = super(AttributeThunk, self).get_form_kwargs()
        kwargs.update(self._viewset.get_form_kwargs())
        return kwargs

    def get_permission_required(self):
        actions = {
            'PopupCreateView': 'create',
            'PopupUpdateView': 'update',
            'PopupDeleteView': 'delete'
        }
        return self._viewset.get_permission_required(actions[self.__class__.__name__])


class TemplateNameMixin(object):
    """
    Get attr template_name_create to PopupCreateView
    Get attr template_name_update to PopupUpdateView
    """

    def get_template_names(self):
        templates = super(TemplateNameMixin, self).get_template_names()
        if self.__class__.__name__ == 'PopupCreateView':
            template_attr_name = 'template_name_create'
        else:
            template_attr_name = 'template_name_update'
        if hasattr(self._viewset, template_attr_name):
            templates.insert(0, getattr(self._viewset, template_attr_name))
        return templates


class PopupCreateView(AttributeThunk, TemplateNameMixin, PermissionRequiredMixin, CreateView):

    def get_context_data(self, **kwargs):
        if 'to_field' in self.request.GET:
            kwargs['to_field'] = self.request.GET['to_field']
        kwargs['popup_name'] = self.request.GET['popup_name']
        return super(PopupCreateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        context = {'op': 'create', 'id': self.object.id, 'value': self.object.__str__()}
        if 'to_field' in self.request.GET:
            context['to_field'] = self.request.GET['to_field']
        return TemplateResponse(self.request, 'popup/success.html', context=context)


class PopupUpdateView(AttributeThunk, TemplateNameMixin, PermissionRequiredMixin, UpdateView):
    slug_field = 'id'
    context_object_name = 'popup'

    def get_context_data(self, **kwargs):
        if 'to_field' in self.request.GET:
            kwargs['to_field'] = self.request.GET['to_field']
        kwargs['popup_name'] = self.request.GET['popup_name']
        return super(PopupUpdateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        context = {'op': 'update', 'id': self.object.id, 'value': self.object.__str__()}
        if 'to_field' in self.request.GET:
            context['to_field'] = self.request.GET['to_field']
        return TemplateResponse(self.request, 'popup/success.html', context=context)


class PopupDeleteView(AttributeThunk, PermissionRequiredMixin, DeleteView):
    slug_field = 'id'

    def delete(self, request, *args, **kwargs):
        if not self.model:
            raise ImproperlyConfigured('model must be override in PopupDeleteView')

        self.object = self.get_object()
        data = {'op': 'delete', 'id': self.object.id, 'value': self.object.__str__()}
        self.object.delete()
        return JsonResponse(data=data)


class PopupCRUDViewSet(object):
    model = None
    fields = ()
    form_class = None
    """
    permissions_required = {
        'create': ('post.add_category',),
        'update': ('post.update_category',),
        'delete': ('post.delete_category',)
    }
    """
    raise_exception = True
    permissions_required = {}

    @classonlymethod
    def _generate_view(cls, crud_view_class, **initkwargs):
        def view(request, *args, **kwargs):
            initkwargs['request'] = request
            view = crud_view_class(cls, **initkwargs)
            if hasattr(view, 'get') and not hasattr(view, 'head'):
                view.head = view.get
            view.request = request
            view.args = args
            view.kwargs = kwargs
            return view.dispatch(request, *args, **kwargs)

        view.view_class = crud_view_class
        view.view_initkwargs = initkwargs

        # take name and docstring from class
        # update_wrapper(view, crud_view_class, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        # update_wrapper(view, crud_view_class.dispatch, assigned=())
        return view

    @classonlymethod
    def create(cls, **initkwargs):
        """Returns the create view that can be specified as the second argument
        to url() in urls.py.
        """
        return cls._generate_view(PopupCreateView, **initkwargs)

    @classonlymethod
    def update(cls, **initkwargs):
        """Returns the update view that can be specified as the second argument
        to url() in urls.py.
        """
        return cls._generate_view(PopupUpdateView, **initkwargs)

    @classonlymethod
    def delete(cls, **initkwargs):
        """Returns the delete view that can be specified as the second argument
        to url() in urls.py.
        """
        return cls._generate_view(PopupDeleteView, **initkwargs)

    def get_form_kwargs(self):
        """
        For Create and Update views, this method allows passing custom arguments
        to the form class constructor. The return value from this method is
        combined with the default form constructor ``**kwargs`` before it is
        passed to the form class' ``__init__()`` routine's ``**kwargs``.

        Since Django CBVs use kwargs ``initial`` & ``instance``, be careful
        when using these, unless of course, you want to override the objects
        provided by these keys.
        """
        return {}

    @classonlymethod
    def urls(cls):
        """
        generate url and url_name for create、update and delete view
        default url_name is classname_
        """
        class_name = cls.model.__name__.lower()
        return path('{}/'.format(class_name), include([
            path('popup/', cls.create(), name='{}_popup_create'.format(class_name)),
            path('popup/<int:pk>/', cls.update(), name='{}_popup_update'.format(class_name)),
            path('popup/delete/<int:pk>/', cls.delete(), name='{}_popup_delete'.format(class_name)),
        ]))

    @classonlymethod
    def get_fk_popup_field(cls):
        """
        generate fk field related to class wait popup crud
        :param request:
        :return:
        """
        class_name = cls.model.__name__.lower()
        class_verbose_name = cls.model._meta.verbose_name
        return ForeignKeyWidget('{}_popup_create'.format(class_name),
                                **{'popup_name': class_verbose_name, 'permissions_required': cls.permissions_required})

    @classonlymethod
    def get_m2m_popup_field(cls):
        """
        generate m2m field related to class wait popup crud
        :param model_class:
        :return:
        """
        class_name = cls.model.__name__.lower()
        class_verbose_name = cls.model._meta.verbose_name
        return ManyToManyWidget('{}_popup_create'.format(class_name),
                                **{'popup_name': class_verbose_name, 'permissions_required': cls.permissions_required})

    def get_permission_required(self, action):
        """
        Return the permission required for the CRUD operation specified in op.
        Default implementation returns the value of one
        ``{list|create|detail|update|delete}_permission_required`` class attributes.
        Overriding this allows you to return dynamically computed permissions.

        :param op: The CRUD operation code. One of
            ``{'list'|'create'|'detail'|'update'|'delete'}``.
        """
        return self.permissions_required.get(action, [])
