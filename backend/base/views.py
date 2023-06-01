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
    data = ['', 'api/login', 'api/models',
            'api/register', 'api/model_generate']
    return JsonResponse(data, safe=False)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=HTTP_404_NOT_FOUND)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=HTTP_200_OK)


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
        if models:
          for model in models:
            model.priority = model.priority + 1
            model.save()
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
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return Response({'message': 'User created successfully!'})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def User_logout(request):
    request.user.auth_token.delete()
    logout(request)
    return Response('User logged out successfully!')


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def Model_generator(request):
    body = json.loads(request.body)
    name = body["name"]
    action = body["action"]
    desc = body["description"]
    uuid = body["uuid"]
    parsedData = model_parser.getParsedData(body["json_data"])
    user = request.user
    current_idx = 0
    for each_model in parsedData:
      if action == "save":
          model = Models.objects.create(
              name=body["json_data"]["tables"][current_idx]["name"], description=desc, priority=1, json=body["json_save"], model=each_model, user=user, uuid=uuid)
      current_idx = current_idx + 1
    mm = Models.objects.filter(uuid=uuid)
    serializer = ModelSerializer(mm, many=True)
    print(serializer.data)
    if action == "save":
        return Response({'message': 'Models created and Project saved successfully!', 'model': serializer.data})
    else:
      models = []
      current_idx = 0
      for each_model in parsedData:
        models.append({'name': body["json_data"]["tables"][current_idx]["name"], 'model': each_model})
        current_idx = current_idx + 1
      return Response({'message': 'Model created successfully!', 'model': models})


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
    return Response({'message': 'Projects fetched successfully', 'model': data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_model(request):
    data = json.loads(request.body)
    # id = data["id"]
    name = data["name"]
    desc = data["description"]
    json_data = data["json_data"]
    uuid = data["uuid"]
    # print("PREVIOUS UUID:", uuid)
    parsedData = model_parser.getParsedData(data["json_data"])
    user = request.user
    current_models = Models.objects.filter(uuid=uuid)
    current_models.delete()
    current_priority = 1
    if current_models:
      current_priority = current_models[0].priority
    current_idx = 0
    for each_model in parsedData:
      # TODO: add previous priority here, currently set to 1
      print("model created")
      model = Models.objects.create(
          name=data["json_data"]["tables"][current_idx]["name"], description=desc, priority=current_priority, json=data["json_save"], model=each_model, user=user, uuid=uuid)
      current_idx = current_idx + 1
    mm = Models.objects.filter(uuid=uuid)
    serializer = ModelSerializer(mm, many=True)
    # print(mm)
    return Response({'message': 'Models updated successfully', 'model': serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_model(request):
    data = json.loads(request.body)
    uuid = data["uuid"]
    user = request.user
    models = Models.objects.filter(uuid=uuid)
    models.delete()
    return Response({'message': 'Project deleted successfully!'})
