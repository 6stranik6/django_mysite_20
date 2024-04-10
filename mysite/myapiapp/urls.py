from django.urls import path

from .views import GroupsListView


app_name = 'myapiapp'

urlpatterns = [
    path('groups/', GroupsListView.as_view(), name='groups')
]