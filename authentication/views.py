from django.http import JsonResponse
from .models import CustomUser, UserProfile
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils import get_tokens_for_user, error_response
from django.db import DatabaseError
import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@csrf_exempt
def signup(request):
    print(request.method)
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            username = request.POST.get('username')
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            print(email, username)
            if password != confirm_password:
                return error_response('Passwords do not match')

            if CustomUser.objects.filter(email=email).exists():
                return error_response('Email already exists')

            user = CustomUser.objects.create_user(email=email, username=username, phone_number=phone_number, password=password, is_active=True)
            print(user)
            return render(request, 'registration/default/auth-login.html')
        except DatabaseError as e:
            return JsonResponse({'error': f'Database error: {e}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)
    return render(request, 'registration/default/auth-register.html')


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email is None or password is None:
            return error_response('Email and password REQUIRED!')
        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                try:
                    profile = user.userprofile  # Assuming UserProfile is related as user.userprofile
                except UserProfile.DoesNotExist:
                    profile = None
                # user_data = {
                #     'id': user.id,
                #     'email': user.email,
                #     'username': user.username,
                #     'phone_number':user.phone_number,
                # }
                # token = get_tokens_for_user(user)
                if profile and profile.business_description and profile.industry and profile.location:
                    return redirect(reverse('dashboard'))  # Redirect to tabs page if profile is complete
                else:
                    return redirect(reverse('profile'))
            else:
                return JsonResponse({'error': 'Account is not activated yet!'}, status=401)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    return render(request, 'registration/default/auth-login.html')

def signout(request):
    logout(request)
    return redirect('/')


@csrf_exempt
def profile(request):
    if request.method == 'POST':
        # Handle form submission and save data to UserProfile model
        business_description = request.POST.get('business_description', '')
        industry = request.POST.get('industry', '')
        location = request.POST.get('location', '')
        
        # Create a new UserProfile for the current user
        user_profile = UserProfile.objects.create(
            user=request.user,
            business_description=business_description,
            industry=industry,
            location=location
        )
        
        return render(request, 'dashboard/home.html')
     
    return render(request, 'dashboard/profile.html')
    
def tabs_page(request):
    return render(request, 'dashboard/tabs.html')

@csrf_exempt
@login_required
def dashboard(request):
    return render(request, 'dashboard/home.html')