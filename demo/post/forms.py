from django import forms
from .popups import CategoryPopupCRUDViewSet, TagPopupCRUDViewSet

from .models import *


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.request = request
        self.fields['tags'].widget.request = request
        self.fields['title'].widget.attrs.update({'class': 'layui-input'})
        self.fields['category'].widget.attrs.update({'class': 'layui-input', 'lay-ignore': ''})
        self.fields['tags'].widget.attrs.update({'class': 'layui-textarea', 'lay-ignore': ''})

    class Meta:
        model = Post
        fields = ['title', 'category', 'tags']
        widgets = {
            'category': CategoryPopupCRUDViewSet.get_fk_popup_field(),
            'tags': TagPopupCRUDViewSet.get_m2m_popup_field(),
        }
