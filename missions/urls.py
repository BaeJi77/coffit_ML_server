from django.urls import path

from . import apis

urlpatterns = [
    path('', apis.post_list),
]