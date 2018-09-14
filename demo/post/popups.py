from django import forms
from popup_field.views import PopupCRUDViewSet
from django.contrib.auth.mixins import AccessMixin

from .models import *


class IsStaffUserMixin(AccessMixin):
    """
    request must be staff
    """
    raise_exception = True
    permission_denied_message = 'You are not a staff'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(IsStaffUserMixin, self).dispatch(request, *args, **kwargs)


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'layui-input'})

    class Meta:
        model = Category
        fields = ['name']


class TagForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'layui-input'})

    class Meta:
        model = Tag
        fields = ['name']


class CategoryPopupCRUDViewSet(PopupCRUDViewSet):
    model = Category
    form_class = CategoryForm
    # parent_class = IsStaffUserMixin
    # template_name_create = 'popup/create.html'
    # template_name_update = 'popup/update.html'


class TagPopupCRUDViewSet(PopupCRUDViewSet):
    model = Tag
    form_class = TagForm
    # parent_class = IsStaffUserMixin
    # template_name_create = 'popup/create.html'
    # template_name_update = 'popup/update.html'
