import datetime
import random
import string

from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user_app.models import User, ConfirmationCode
from user_app.permissions import IsAdmin
from user_app.serializers import UserSerializer


def sms_token():
    return ''.join([random.choice(string.ascii_letters) for x in range(20)])


@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)

        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'data': 'Пользователь не найден'})
        else:
            token = None
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                pass
            if token is None:
                token = Token.objects.create(user=user)
                token.save()
            if user.is_active:
                return Response({
                    'token': token.key,
                    'user': {
                        'id': user.pk,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'username': user.username,
                        'user_type': user.user_type,
                        # 'avatar': user.avatar,
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={'data': 'Профиль не активирован'}, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reauth_view(request):
    if request.method == 'GET':
        user = request.user
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'data': 'Пользователь не найден'})
        else:
            token = Token.objects.get(user=user)
            if user.is_active:
                return Response({
                    'token': token.key,
                    'user': {
                        'id': user.pk,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'username': user.username,
                        'user_type': user.user_type,
                        # 'avatar': user.avatar,
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={'data': 'Профиль не активирован'}, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['GET'])
@permission_classes([IsAdmin])
def profile_list_view(request):
    if request.method == 'GET':
        profile_list = User.objects.filter(is_active=True, user_type__in=[2, 3])
        return Response(status=status.HTTP_200_OK, data=UserSerializer(profile_list, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdmin])
def add_profile_view(request):
    if request.method == 'POST':
        username = request.data['username']
        password = request.data['password']
        user = User.objects.create_user(username=username, email='', password=password)
        try:
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            user.first_name = first_name
            user.last_name = last_name
        except:
            pass
        user.email = request.data.get('email', 't@m.ru')
        user.phone = request.data.get('phone', '+996 700 121212')
        user.user_type = int(request.data.get('user_type', 2))
        user.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAdmin])
def edit_profile_view(request, id):
    if request.method == 'PUT':
        user = User.objects.get(id=id)
        try:
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            user.first_name = first_name
            user.last_name = last_name
        except:
            pass
        user.username = request.data.get('username', '')
        user.email = request.data.get('email', 't@m.ru')
        user.user_type = int(request.data.get('role', 1))
        user.phone = request.data.get('phone', '+996 700 121212')
        user.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
def auth_register(request):
    if request.method == 'POST':
        username = request.data['username']
        password = request.data['password']
        user = None
        try:
            user = User.objects.get(username=username)
        except:
            pass
        if user is not None:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        user = User.objects.create(username=username, last_name='', first_name='')
        try:
            first_name = request.data.get('first_name', '')
            user.first_name = first_name

        except:
            pass
        try:
            last_name = request.data.get('last_name', '')
            user.last_name = last_name
        except:
            pass
        user.user_type = request.data.get('user_type', 3)
        user.is_active = False
        user.set_password(password)
        user.save()
        until = datetime.datetime.now() + datetime.timedelta(minutes=60)
        token = ConfirmationCode.objects.create(user=user, token=sms_token(),
                                                valid_until=until)
        token.save()

        email = EmailMessage('IziShop - Код подтверждения', 'Пройдите по ссылке \n '
                                                            'http://izi.pixelkalpak.com/confirm/%s'
                             % token.token,
                             to=[username])
        email.send()
        return Response(status=status.HTTP_201_CREATED, data={'data': 'Пользователь создан'})


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_user(request, code):
    if request.method == 'POST':
        try:
            token = ConfirmationCode.objects.get(token=code,
                                                 valid_until__gte=datetime.datetime.now())
            token.user.is_active=True
            token.user.save()
            token.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except ConfirmationCode.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def profile_resend_code_view(request):
    try:
        user = User.objects.get(username=request.data.get('email'))
        try:
            ConfirmationCode.objects.get(user=user,
                                         valid_until__gte=datetime.datetime.now()).delete()
        except:
            pass
        until = datetime.datetime.now() + datetime.timedelta(minutes=60)
        token = ConfirmationCode.objects.create(user=user, token=sms_token(),
                                                valid_until=until)
        email = EmailMessage('IziShop - Код подтверждения', 'Пройдите по ссылке \n '
                                                            'http://izi.pixelkalpak.com/confirm/%s' % token.token,
                             to=[user.username])
        email.send()
        return Response(status=status.HTTP_200_OK, data={'data': 'Код отправлен на почту'})
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
