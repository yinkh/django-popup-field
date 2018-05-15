from django.urls import path, include
from .views import *

urlpatterns = [
    path('', PostCreateView.as_view(), name='post_create'),

    CategoryPopupCRUDViewSet.urls(),
    TagPopupCRUDViewSet.urls(),
]
