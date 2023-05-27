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
import json
from django.db import models
import inspect
from . import model_parser
import json
# Create your views here.

# Replace with your JSON data
json_data = """
{
  "tables": [
    {
      "name": "table1",
      "columns": [
        {
          "name": "id",
          "type": "integer",
          "primary_key": true,
          "max_length": 255
        },
        {
          "name": "name",
          "type": "string",
          "max_length": 255
        }
      ]
    },
    {
      "name": "table2",
      "columns": [
        {
          "name": "id",
          "type": "integer",
          "primary_key": true
        },
        {
          "name": "title",
          "type": "string",
          "max_length": 255
        },
        {
          "name": "description",
          "type": "text"
        }
      ]
    }
  ]
}
"""

def endpoints(request):
    data = ['', 'api/login', 'api/models', 'api/register', 'api/model_generate']
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

@api_view(['POST'])
@permission_classes((AllowAny,))
def getAllModels(request):
    if request.method == "POST":
        models = Models.objects.all().order_by('-priority')
        serializer = ModelSerializer(models, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def getModelById(request):
    if request.method == "POST":
        body = json.loads(request.body)
        uuid = body["uuid"]
        models = Models.objects.filter(uuid=uuid)
        serializer = ModelSerializer(models, many=True)
        print(serializer.data)
        return Response(serializer.data, status=HTTP_200_OK)


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
        user = User(username=username,email=email)
        user.set_password(password)
        user.save()
        return Response({'message': 'User Created Successfully'})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def User_logout(request):
    request.user.auth_token.delete()
    logout(request)
    return Response('User Logged out successfully')

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def Model_generator(request):    
    body = json.loads(request.body)
    name = body["name"]
    action = body["action"]
    desc = body["description"]
    uuid = body["uuid"]
    print(body["json_data"])
    parsedData = model_parser.getParsedData(body["json_data"])
    user = request.user
    print(parsedData)
    for each_model in parsedData:
      if action == "save":
        model = Models.objects.create(name=name, priority=1, json=json_data, model=each_model, user=user, uuid=uuid)
    mm = Models.objects.filter(uuid=uuid)
    serializer = ModelSerializer(mm, many=True)
    print(mm)
    if action == "save":
      return Response({'message': 'Model Created and Saved Successfully', 'model' : serializer.data})
    else:
      return Response({'message': 'Model Created Successfully', 'model' : parsedData})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_models(request):    
    user = request.user
    models = Models.objects.filter(user=user)
    serializer = ModelSerializer(models, many=True)
    data = {}
    for i in serializer.data:
      if i['uuid'] in data:
        data[i['uuid']].append(i)
      else:
        data[i['uuid']] = [i]
    return Response({'message': 'Model Fetched Successfully', 'model' : data})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_model(request):   
    data = json.loads(request.body)
    id = data["id"] 
    name = data["name"]
    desc = data["description"]
    json_data = data["json_data"]
    uuid = data["uuid"]
    user = request.user
    models = Models.objects.get(uuid=uuid)
    models.name = name
    models.description = desc
    models.json = json_data
    parsedData = model_parser.getParsedData(body["json_data"])
    models.save()
    serializer = ModelSerializer(models, many=True)
    return Response({'message': 'Model Updated Successfully', 'model' : serializer.data})
        
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_model(request):   
    data = json.loads(request.body)
    id = data["id"] 
    user = request.user
    models = Models.objects.get(id=id)
    models.json = json_data
    models.delete()
    return Response({'message': 'Model Deleted Successfully'})