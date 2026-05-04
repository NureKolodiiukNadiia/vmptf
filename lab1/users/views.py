from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages

from .forms import LoginForm, RegistrationForm
from .services import AuthService


class LoginView(DjangoLoginView):
    form_class = LoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('visitor:active_visits')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)


class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('visitor:active_visits')
    
    def form_valid(self, form):
        user = AuthService.register_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            raw_password=form.cleaned_data['password1'],
            role=form.cleaned_data['role'],
            first_name=form.cleaned_data.get('first_name', ''),
            last_name=form.cleaned_data.get('last_name', '')
        )
        
        login(self.request, user)
        
        messages.success(
            self.request,
            f'Account created successfully! Welcome, {user.username}.'
        )
        
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below')
        return super().form_invalid(form)

def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {username}!')
    return redirect('users:login')
