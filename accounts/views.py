from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView

from .forms import CustomUserCreationForm
from .models import User, Darts

# Create your views here.


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You must log in to view your profile.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("tournaments:list-tournaments")
    else:
        form = AuthenticationForm(request)
    context = {
        "form": form
    }
    return render(request, "accounts/login.html", context)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("accounts:login")
    return render(request, "accounts/logout.html", {})


class EditProfile(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['email', 'username', 'first_name', 'last_name', 'city', 'country', 'time_zone']
    template_name = 'accounts/edit_profile.html'
    success_message = 'Changes successfully saved'

    def get_object(self):
        obj = get_object_or_404(User, pk=self.request.user.pk)
        return obj

    def form_valid(self, form):
        messages.success(self.request, f"Your profile has been saved.")  # {m}")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'edit profile'
        return context

    def get_success_url(self):
        return '/account/edit/'


# TODO all tables by darts here and in DartsListView, AllDartsListView
class DartsDetailView(DetailView):
    model = Darts

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'darts-detail'
        return context


class CreateDarts(LoginRequiredMixin, CreateView):
    context_object_name = 'Create'
    model = Darts
    fields = ['name', 'weight', 'description', 'picture', 'active']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'create-darts'
        return context


class DartsUpdateView(LoginRequiredMixin, UpdateView):
    context_object_name = 'Update'
    model = Darts
    fields = ['name', 'weight', 'description', 'picture', 'active']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'edit-darts'
        return context


class DartsDeleteView(LoginRequiredMixin, DeleteView):
    model = Darts
    success_url = reverse_lazy('accounts:list-darts')


class DartsListView(ListView):
    model = Darts

    def get_queryset(self):
        return Darts.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'darts'
        return context


class AllDartsListView(ListView):
    model = Darts
    paginate_by = 20
    template_name = 'accounts/all_darts_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'all darts'
        return context
