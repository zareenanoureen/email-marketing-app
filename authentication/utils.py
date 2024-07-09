from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

def error_response(message, status=400):
    return JsonResponse({'error': message}, status=status)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }