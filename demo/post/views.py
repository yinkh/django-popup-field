from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import *
from .models import *


class PostCreateView(CreateView):
    raise_exception = True
    form_class = PostForm
    template_name = 'post/create.html'
    success_url = reverse_lazy('post_create')

    def get_form_kwargs(self):
        kwargs = super(PostCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
