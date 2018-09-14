## django-popup-field
A popup field for django which can create\update\delete ForeignKey and ManyToManyField instance by popup windows.

### Requirements
- Python3
- Django

### Demo
![popup demo](https://www.yinkh.top/media/summer_note/20180515-170605-512.gif)

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
		    template_name_create = 'popup/create.html'
		    template_name_update = 'popup/update.html'
		    permissions_required = {
		        'create': ('post.add_category',),
		        'update': ('post.update_category',),
		        'delete': ('post.delete_category',)
		    }

	    class TagPopupCRUDViewSet(PopupCRUDViewSet):
		    model = Tag
		    form_class = TagForm
		    template_name_create = 'popup/create.html'
		    template_name_update = 'popup/update.html'


4. Change widget for category and tag used in `forms.py`:

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

	And you need include button css in 'post/create.html' like:

        {% load static %}
        <link rel="stylesheet" href="{% static 'popup_field/button.css' %}">
6. Custom your popup template, `popup/create.html`:

        {% extends "popup/base.html" %}
        {% block css %}
        {% endblock %}

        {% block js %}
        {% endblock %}

        {% block main %}
            <div class="layui-container" style="margin: 4px">
                <form class="layui-form" enctype="multipart/form-data"
                      action="{{ request.path }}{% if to_field %}?to_field={{ to_field }}{% endif %}"
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

    `popup/update.html`:

        {% extends "popup/base.html" %}

        {% block css %}
        {% endblock %}

        {% block js %}
        {% endblock %}

        {% block main %}
            <div class="layui-container" style="margin: 4px">
                <form class="layui-form" enctype="multipart/form-data"
                      action="{{ request.path }}{% if to_field %}?to_field={{ to_field }}{% endif %}"
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

	The `object_name` inside template always is `popup`.The point is you must append `{% if to_field %}?to_field={{ to_field }}{% endif %}` in form action or keep set as `"{{ request.path }}{% if to_field %}?to_field={{ to_field }}{% endif %}"`.
7. All url for popup create\update\delete is generate by `PopupCRUDViewSet`, `urls.py` :

		from .views import *

		urlpatterns = [
		    path('', PostCreateView.as_view(), name='post_create'),

		    CategoryPopupCRUDViewSet.urls(),
		    TagPopupCRUDViewSet.urls(),
		]

	this will register the following urls:

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

### Advance
#### Set default `template_name_create` and `template_name_update`
`template_name_create` is the template used for create popup window, `template_name_update` is the template used for update popup window.

You can set default `template_name_create` and `template_name_update` in settings like:

    POPUP_TEMPLATE_NAME_CREATE = 'popup/create.html'
    POPUP_TEMPLATE_NAME_UPDATE = 'popup/update.html'

`PopupCRUDViewSet` will use this as default `template_name_create` and `template_name_update` if you don't have a special assignment in `PopupCRUDViewSet`.

#### Override template for `PopupCreateView` and `PopupUpdateView` in `PopupCRUDViewSet`
    class CategoryPopupCRUDViewSet(PopupCRUDViewSet):
	    ...
	    template_name_create = 'popup/create.html'
	    template_name_update = 'popup/update.html'

    class TagPopupCRUDViewSet(PopupCRUDViewSet):
	    ...
	    template_name_create = 'popup/create.html'
	    template_name_update = 'popup/update.html'


#### Override template for `ForeignKeyWidget` and `ManyToManyWidget`
If you want override template used by `ForeignKeyWidget` and `ManyToManyWidget`,you have to way to achieve this,first one is:

	class PopupCRUDViewSet(object):
	    ...
	    template_name_fk = 'popup/foreign_key_select.html'
	    template_name_m2m = 'popup/many_to_many_select.html'
second one is:

    class PostForm(forms.ModelForm):
        ...

        class Meta:
            model = Post
            fields = ['title', 'category', 'tags']
            widgets = {
                'category':CategoryPopupCRUDViewSet.get_fk_popup_field(template_name='popup/foreign_key_select.html')
                'tags': TagPopupCRUDViewSet.get_m2m_popup_field(template_name='popup/many_to_many_select.html'),
            }

#### Set parent class for `PopupCreateView、PopupUpdateView、PopupDeleteView` in `PopupCRUDViewSet`
You can set parent class for `PopupCreateView、PopupUpdateView、PopupDeleteView` in `PopupCRUDViewSet` like:

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

	class CategoryPopupCRUDViewSet(PopupCRUDViewSet):
	    model = Category
	    form_class = CategoryForm
	    parent_class = IsStaffUserMixin

	class TagPopupCRUDViewSet(PopupCRUDViewSet):
	    model = Tag
	    form_class = TagForm
	    parent_class = IsStaffUserMixin

The usage is set common permission check for `PopupCreateView、PopupUpdateView、PopupDeleteView`. In demo we will check whether the operator is a staff.