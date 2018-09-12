import django

from django.forms.widgets import Select, SelectMultiple

if django.VERSION >= (2, 0):
    from django.urls import reverse_lazy
else:
    from django.core.urlresolvers import reverse_lazy


class ForeignKeyWidget(Select):
    template_name = 'widgets/foreign_key_select.html'

    def __init__(self, url_template, *args, **kwargs):
        self.template_name = kwargs.pop('template_name', self.template_name)
        self.popup_name = kwargs.pop('popup_name', '')
        self.permissions_required = kwargs.pop('permissions_required', '')
        self.request = kwargs.pop('request', None)
        self.width = kwargs.pop('width', '700px')
        self.height = kwargs.pop('height', '500px')
        self.url_template = reverse_lazy(url_template)
        super(ForeignKeyWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super(ForeignKeyWidget, self).get_context(name, value, attrs)
        context['popup_name'] = self.popup_name
        context['width'] = self.width
        context['height'] = self.height
        context['add_url'] = self.url_template
        context['update_url'] = self.url_template
        context['delete_url'] = self.url_template + 'delete/'
        if self.request is not None:
            context['can_add'] = self.request.user.has_perms(self.permissions_required.get('create', []))
            context['can_update'] = self.request.user.has_perms(self.permissions_required.get('update', []))
            context['can_delete'] = self.request.user.has_perms(self.permissions_required.get('delete', []))
        else:
            context['can_add'] = True
            context['can_update'] = True
            context['can_delete'] = True
        return context


class ManyToManyWidget(SelectMultiple):
    template_name = 'widgets/many_to_many_select.html'

    def __init__(self, url_template, *args, **kwargs):
        self.template_name = kwargs.pop('template_name', self.template_name)
        self.popup_name = kwargs.pop('popup_name', '')
        self.permissions_required = kwargs.pop('permissions_required', '')
        self.request = kwargs.pop('request', None)
        self.width = kwargs.pop('width', '700px')
        self.height = kwargs.pop('height', '500px')
        self.url_template = reverse_lazy(url_template)
        super(ManyToManyWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super(ManyToManyWidget, self).get_context(name, value, attrs)
        context['popup_name'] = self.popup_name
        context['width'] = self.width
        context['height'] = self.height
        context['add_url'] = self.url_template
        context['update_url'] = self.url_template
        context['delete_url'] = self.url_template + 'delete/'
        if self.request is not None:
            context['can_add'] = self.request.user.has_perms(self.permissions_required.get('create', []))
            context['can_update'] = self.request.user.has_perms(self.permissions_required.get('update', []))
            context['can_delete'] = self.request.user.has_perms(self.permissions_required.get('delete', []))
        else:
            context['can_add'] = True
            context['can_update'] = True
            context['can_delete'] = True
        return context
