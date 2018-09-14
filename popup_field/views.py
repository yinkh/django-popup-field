import django
from django.conf import settings
from django.utils.decorators import classonlymethod
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import JsonResponse
from django.template.response import TemplateResponse
from django.core.exceptions import ImproperlyConfigured
from .fields import ForeignKeyWidget, ManyToManyWidget

if django.VERSION >= (2, 0):
    from django.urls import path, include
else:
    from django.conf.urls import url, include


class PopupCreateView(PermissionRequiredMixin, CreateView):
    popup_name = None

    def get_context_data(self, **kwargs):
        if 'to_field' in self.request.GET:
            kwargs['to_field'] = self.request.GET['to_field']
        kwargs['popup_name'] = self.popup_name
        return super(PopupCreateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        context = {'op': 'create', 'id': self.object.id, 'value': self.object.__str__()}
        if 'to_field' in self.request.GET:
            context['to_field'] = self.request.GET['to_field']
        return TemplateResponse(self.request, 'popup/success.html', context=context)


class PopupUpdateView(PermissionRequiredMixin, UpdateView):
    slug_field = 'id'
    context_object_name = 'popup'
    popup_name = None

    def get_context_data(self, **kwargs):
        if 'to_field' in self.request.GET:
            kwargs['to_field'] = self.request.GET['to_field']
        kwargs['popup_name'] = self.popup_name
        return super(PopupUpdateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        context = {'op': 'update', 'id': self.object.id, 'value': self.object.__str__()}
        if 'to_field' in self.request.GET:
            context['to_field'] = self.request.GET['to_field']
        return TemplateResponse(self.request, 'popup/success.html', context=context)


class PopupDeleteView(PermissionRequiredMixin, DeleteView):
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
    form_class = None
    class_name = None
    class_verbose_name = None
    template_name_create = None
    template_name_update = None
    template_name_fk = None
    template_name_m2m = None
    context_for_create = {}
    context_for_update = {}
    # parent class for PopupCreateView、PopupUpdateView、PopupDeleteView
    parent_class = object
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
    def get_template_name_create(cls):
        if cls.template_name_create is None:
            template_name = getattr(settings, 'POPUP_TEMPLATE_NAME_CREATE', None)
            if template_name is None:
                raise ImproperlyConfigured('You must set template_name_create in PopupCRUDViewSet or '
                                           'set POPUP_TEMPLATE_NAME_CREATE in django settings')
            else:
                return template_name
        else:
            return cls.template_name_create

    @classonlymethod
    def get_template_name_update(cls):
        if cls.template_name_update is None:
            template_name = getattr(settings, 'POPUP_TEMPLATE_NAME_UPDATE', None)
            if template_name is None:
                raise ImproperlyConfigured('You must set template_name_update in PopupCRUDViewSet or '
                                           'set POPUP_TEMPLATE_NAME_UPDATE in django settings')
            else:
                return template_name
        else:
            return cls.template_name_update

    @classonlymethod
    def get_class_name(cls):
        if cls.class_name is None:
            return cls.model.__name__.lower()
        else:
            return cls.class_name

    @classonlymethod
    def get_class_verbose_name(cls):
        if cls.class_verbose_name is None:
            return cls.model._meta.verbose_name
        else:
            return cls.class_verbose_name

    @classonlymethod
    def create(cls):
        """
        Returns the create view that can be specified as the second argument
        to url() in urls.py.
        """

        class NewPopupCreateView(PopupCreateView, cls.parent_class):
            model = cls.model
            form_class = cls.form_class
            popup_name = cls.get_class_verbose_name()
            template_name = cls.get_template_name_create()
            permission_required = cls.get_permission_required('create')

            def get_context_data(self, **kwargs):
                kwargs.update(cls.context_for_create)
                return super(NewPopupCreateView, self).get_context_data(**kwargs)

        return NewPopupCreateView

    @staticmethod
    def create_view_context(self, kwargs):
        return kwargs

    @classonlymethod
    def update(cls):
        """
        Returns the update view that can be specified as the second argument
        to url() in urls.py.
        """

        class NewPopupUpdateView(PopupUpdateView, cls.parent_class):
            model = cls.model
            form_class = cls.form_class
            popup_name = cls.get_class_verbose_name()
            template_name = cls.get_template_name_update()
            permission_required = cls.get_permission_required('update')

            def get_context_data(self, **kwargs):
                kwargs.update(cls.context_for_update)
                return super(NewPopupUpdateView, self).get_context_data(**kwargs)

        return NewPopupUpdateView

    @classonlymethod
    def delete(cls):
        """
        Returns the delete view that can be specified as the second argument
        to url() in urls.py.
        """

        class PopupDeleteViewView(PopupDeleteView, cls.parent_class):
            model = cls.model
            form_class = cls.form_class
            permission_required = cls.get_permission_required('delete')

        return PopupDeleteViewView

    @classonlymethod
    def urls(cls):
        """
        generate url and url_name for create、update and delete view
        default url_name is classname_name
        """
        class_name = cls.get_class_name()
        if django.VERSION >= (2, 0):
            return path('{}/'.format(class_name), include([
                path('popup/', cls.create().as_view(), name='{}_popup_create'.format(class_name)),
                path('popup/<int:pk>/', cls.update().as_view(), name='{}_popup_update'.format(class_name)),
                path('popup/delete/<int:pk>/', cls.delete().as_view(), name='{}_popup_delete'.format(class_name)),
            ]))
        else:
            return url(r'^{}/'.format(class_name), include([
                url(r'^popup/$', cls.create().as_view(), name='{}_popup_create'.format(class_name)),
                url(r'^popup/(?P<pk>\d+)/$', cls.update().as_view(), name='{}_popup_update'.format(class_name)),
                url(r'^popup/delete/(?P<pk>\d+)/$', cls.delete().as_view(), name='{}_popup_delete'.format(class_name)),
            ]))

    @classonlymethod
    def get_fk_popup_field(cls, *args, **kwargs):
        """
        generate fk field related to class wait popup crud
        """
        kwargs['popup_name'] = cls.get_class_verbose_name()
        kwargs['permissions_required'] = cls.permissions_required
        if cls.template_name_fk is not None:
            kwargs['template_name'] = cls.template_name_fk
        return ForeignKeyWidget('{}_popup_create'.format(cls.get_class_name()), *args, **kwargs)

    @classonlymethod
    def get_m2m_popup_field(cls, *args, **kwargs):
        """
        generate m2m field related to class wait popup crud
        """
        kwargs['popup_name'] = cls.get_class_verbose_name()
        kwargs['permissions_required'] = cls.permissions_required
        if cls.template_name_m2m is not None:
            kwargs['template_name'] = cls.template_name_m2m
        return ManyToManyWidget('{}_popup_create'.format(cls.get_class_name()), *args, **kwargs)

    @classonlymethod
    def get_permission_required(cls, action):
        """
        Return the permission required for the CRUD operation specified in action.
        Default implementation returns the value of one
        """
        return cls.permissions_required.get(action, [])
