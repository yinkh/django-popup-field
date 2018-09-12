import django
from .views import *

if django.VERSION >= (2, 0):
    from django.urls import path, include

    urlpatterns = [
        path('', PostCreateView.as_view(), name='post_create'),

        CategoryPopupCRUDViewSet.urls(),
        TagPopupCRUDViewSet.urls(),
    ]

else:
    from django.conf.urls import url, include

    urlpatterns = [
        url(r'^$', PostCreateView.as_view(), name='post_create'),

        CategoryPopupCRUDViewSet.urls(),
        TagPopupCRUDViewSet.urls(),
    ]
