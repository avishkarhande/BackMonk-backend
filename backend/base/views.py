from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Models
from .serializers import ModelSerializer
from django.contrib.auth.models import User
from django.contrib.auth import logout
# Create your views here.

def endpoints(request):
    data = ['/advocates', 'advocates/:username']
    return JsonResponse(data, safe=False)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and Password'}, status=HTTP_404_NOT_FOUND)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token':token.key}, status=HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def getAllModels(request):
    if request.method == "GET":
        models = Models.objects.filter(user=request.user)
        serializer = ModelSerializer(models, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
    if request.method == "POST":
        name = request.data.get("name")
        json = request.data.get("json")
        user = request.user
        entry = Models(name=name, priority=1, json=json, user=user)
        entry.save()


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def register(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    existing_error = User.objects.filter(username=username)
    if existing_error.exists():
        return Response({}, status=HTTP_200_OK)
    else:
        user = User(username=username,email=email, password=password)
        user.save()
        return Response({'message': 'User Created Successfully'})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def User_logout(request):
    request.user.auth_token.delete()
    logout(request)
    return Response('User Logged out successfully')