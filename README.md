## django-popup-field
A popup field for django which can create\update\delete ForeignKey and ManyToManyField instance by popup windows.

### Requirements
- Python3
- Django >= 2.0

### Demo
You can get a demo in [popup.yinkh.top](http://popup.yinkh.top)

### TODO
- internationalization
- optimize action in form
- css override

### QuickStart

1. Install django-popup-field with pip:

       pip install django-popup-field
    
2. Install the dependencies django-popup-field to INSTALLED_APPS in your project's settings.py:

       INSTALLED_APPS = [
           ...
           'popup_field',
           ...
       ]
3. Assume I have a post app which `models.py` is:

	    class Category(models.Model):
	        name = models.CharField(max_length=255, verbose_name='name')
	    
	        ...
	    
	    
	    class Tag(models.Model):
	        name = models.CharField(max_length=255, verbose_name='name')
	    
	        ...
	    
	    
	    class Post(models.Model):
	        title = models.CharField(max_length=255, verbose_name='title')
	        category = models.ForeignKey('post.Category', related_name='post_category', on_delete=models.CASCADE,
	                                     verbose_name='category')
	        tags = models.ManyToManyField('post.Tag',
	                                      verbose_name='tags')
	        ...
	    
	New `popups.py` in post app,the content is:
	
	    from popup_field.views import PopupCRUDViewSet
	    
	    from .models import *
	    
	    
	    class CategoryForm(forms.ModelForm):
		    class Meta:
		    model = Category
		    fields = ['name']
	    
	    
	    class TagForm(forms.ModelForm):
		    class Meta:
		    model = Tag
		    fields = ['name']
	    
	    
	    class CategoryPopupCRUDViewSet(PopupCRUDViewSet):
		    model = Category
		    form_class = CategoryForm
		    template_name_create = 'popup/category/create.html'
		    template_name_update = 'popup/category/update.html'
		    permissions_required = {
		    'create': ('post.add_category',),
		    'update': ('post.update_category',),
		    'delete': ('post.delete_category',)
		    }
	    
	    class TagPopupCRUDViewSet(PopupCRUDViewSet):
		    model = Tag
		    form_class = TagForm
		    template_name = 'popup/update.html'
		    template_name_create = 'popup/tag/create.html'
		    template_name_update = 'popup/tag/update.html'
        
  	`template_name_create` is the template used for create popup window, `template_name_update` is the template used for update popup window.

4. Change widget category and tag used in `forms.py`:

        from django import forms
	    from .popups import CategoryPopupCRUDViewSet, TagPopupCRUDViewSet
	    
	    from .models import *
	    
	    
	    class PostForm(forms.ModelForm):
		    def __init__(self, *args, **kwargs):
		    request = kwargs.pop('request')
		    super(PostForm, self).__init__(*args, **kwargs)
		    self.fields['category'].widget.request = request
		    self.fields['tags'].widget.request = request
	    
		    class Meta:
			    model = Post
			    fields = ['title', 'category', 'tags']
			    widgets = {
				    'category': CategoryPopupCRUDViewSet.get_fk_popup_field(),
				    'tags': TagPopupCRUDViewSet.get_m2m_popup_field(),
			    }
            
5. The `request` kwarg passed to `form` is used for perms check,Only the request user has corresponding permissions then the corresponding button will showup,this is not necessary.

	If you want check permissions for popup fields,you `views.py` should like:
	
	    class PostCreateView(CreateView):
	        raise_exception = True
	        form_class = PostForm
	        template_name = 'post/create.html'
	        success_url = reverse_lazy('post_create')
	    
	        def get_form_kwargs(self):
	            kwargs = super(PostCreateView, self).get_form_kwargs()
	            kwargs['request'] = self.request
	            return kwargs
6. Custom your popup template, `popup/category/create.html`:

		{% extends "popup/base.html" %}
		{% block css %}
		{% endblock %}
		
		{% block js %}
		{% endblock %}
		
		{% block main %}
		    <div class="layui-container" style="margin: 4px">
		        <form class="layui-form" enctype="multipart/form-data"
		              action="{% url 'category_popup_create' %}{% if to_field %}?to_field={{ to_field }}{% endif %}"
		              method="post">
		            {% csrf_token %}
					{{ form.media }}
					{{ form }}

		            <div class="layui-form-item">
		                <div class="layui-input-block">
		                    <button class="layui-btn">Add</button>
		                </div>
		            </div>
		        </form>
		    </div>
		{% endblock %}

    `popup/category/update.html`:

		{% extends "popup/base.html" %}
		
		{% block css %}
		{% endblock %}
		
		{% block js %}
		{% endblock %}
		
		{% block main %}
		    <div class="layui-container" style="margin: 4px">
		        <form class="layui-form" enctype="multipart/form-data"
		              action="{% url 'category_popup_update' popup.id %}{% if to_field %}?to_field={{ to_field }}{% endif %}"
		              method="post">
		            {% csrf_token %}
					{{ form.media }}
					{{ form }}

		            <div class="layui-form-item">
		                <div class="layui-input-block">
		                    <button class="layui-btn">Edit</button>
		                </div>
		            </div>
		        </form>
		    </div>
		{% endblock %}

	The object_name inside template always is popup.The point is you must append `{% if to_field %}?to_field={{ to_field }}{% endif %}` after action or keep action blank.
7. All url for popup create\update\delete is generate by `PopupCRUDViewSet`, `urls.py` :

		from .views import *
		
		urlpatterns = [
		    path('', PostCreateView.as_view(), name='post_create'),
		
		    CategoryPopupCRUDViewSet.urls(),
		    TagPopupCRUDViewSet.urls(),
		]

	This will register the following urls:

		path('category/', include([
	            path('popup/', cls.create(), name='category_popup_create'),
	            path('popup/<int:pk>/', cls.update(), name='category_popup_update'),
	            path('popup/delete/<int:pk>/', cls.delete(), name='category_popup_delete'),
	        ])

		path('tag/', include([
	            path('popup/', cls.create(), name='tag_popup_create'),
	            path('popup/<int:pk>/', cls.update(), name='tag_popup_update'),
	            path('popup/delete/<int:pk>/', cls.delete(), name='tag_popup_delete'),
	        ])
	        
	        