from django.contrib.auth.views import LoginView
from django.urls import path

from myauth.views import (get_cookie_view, set_cookie_view,
                          get_session_view, set_session_view,
                          logout_view, MyLogoutView,
                          RegisterView, UserDetailView,
                          AboutMiView, UsersListView,
                          UserUpdateView, HelloView
                          )

app_name = "myauth"

urlpatterns = [
    path(
        "login/", LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True
        ),
        name='login'),
    path("logout/", MyLogoutView.as_view(), name='logout'),
    path("aboutme/", AboutMiView.as_view(), name='about-me'),
    path("users/", UsersListView.as_view(), name='user_list'),
    path("users/<int:pk>/", UserDetailView.as_view(), name='user_detail'),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name='user_update'),
    path("register/", RegisterView.as_view(), name='register'),
    path("cookie/get/", get_cookie_view, name='cookie_get'),
    path("cookie/set/", set_cookie_view, name='cookie_set'),
    path("session/get/", get_session_view, name='session_get'),
    path("session/set/", set_session_view, name='session_set'),
    path("hello/", HelloView.as_view(), name='hello')


]
