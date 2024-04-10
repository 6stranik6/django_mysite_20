from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.views.generic.edit import BaseUpdateView
from django.forms import inlineformset_factory
from .forms import UserForm, ProfileForm
from .models import Profile
from django.utils.translation import gettext as _


class AboutMiView(TemplateView,):
    template_name = 'myauth/about_me.html'


class UserDetailView(DetailView):
    template_name = 'myauth/user_detail.html'
    queryset = (
        User.objects
        .select_related()
    )


class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    #form_class = UserForm

    form_class = inlineformset_factory(User, Profile, fields=('avatar', 'bio'))
    template_name = 'myauth/user_update.html'

    def test_func(self):
        return self.request.user.is_staff or self.get_object().pk == self.kwargs['pk']

    def get_success_url(self):
        return reverse('myauth:user_detail', kwargs={'pk': self.kwargs['pk']}
                       )
    queryset = (
        User.objects
        .select_related()
    )


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")
        return render(request, "myauth/login.html")

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")

    return render(request, "myauth/login.html", {"error": "Invalid username or password"})


class UsersListView(ListView):
    model = User
    template_name = 'myauth/user-list.html'
    context_object_name = 'users'


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookies set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar")
    return HttpResponse(f"Session value: {value!r}")


class HelloView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        welcome_message = _("Hello World!")
        return HttpResponse(f"<h1>{welcome_message}</h1")
