from django import forms
from popup_field.views import PopupCRUDViewSet

from .models import *


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
    template_name_create = 'popup/category/create.html'
    template_name_update = 'popup/category/update.html'


class TagPopupCRUDViewSet(PopupCRUDViewSet):
    model = Tag
    form_class = TagForm
    template_name_create = 'popup/tag/create.html'
    template_name_update = 'popup/tag/update.html'
