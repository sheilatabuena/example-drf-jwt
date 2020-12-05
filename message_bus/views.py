""" Views for REST api calls for messages """

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib.auth import authenticate, login

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Message
from .serializers import MessageSerializer
from .utilities import token_user


class JWTLogin(APIView):
    """ This class logs in a user. In a more complete project, it would be located in a user app """

    def post(self, request):
        """ logging in is always a post for security reasons """

        results = {'status': 0}

        username = request.POST.get('username', False)
        password = request.POST.get('password', False)

        if not username or not password:
            results['errors'] = 'Please provide username and password'
            return JsonResponse(results, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if not user or not user.is_active:
            results['errors'] = 'Not a current account'
            return JsonResponse(results, status=status.HTTP_403_FORBIDDEN)

        login(request, user)

        refresh = RefreshToken.for_user(user)

        token = str(refresh.access_token)

        print('testing token_user: '+str(token_user(token)))

        if refresh:
            results['token'] = token
            results['status'] = 1

        else:
            results['errors'] = 'Could not get JWT token'

        return JsonResponse(results, status=status.HTTP_200_OK)



class Messages(APIView):
    """ This is the class for Message views, incudes get method only  """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ an authorized user can get their own messages. Their JWT token was processed
            by the middleware and turned into request.user by the time it gets to the view.

            an authorized staff or superuser could also get another users messages from their
            token
        """

        results = {'status': 0}

        token = request.GET.get('token', False)

        if token and (request.user.is_staff or request.user.is_superuser):
            user = token_user(token)

        else:
            user = request.user

        messages = Message.objects.filter(user=user)

        if messages:

            serializer = MessageSerializer(messages, many=True)

            results['count'] = len(messages)
            results['data'] = serializer.data
            results['status'] = 1

        else:
            results['count'] = 0
            results['status'] = 1

        return JsonResponse(results, status=status.HTTP_200_OK)


    def post(self, request, mid=None):
        """ a staff member or admin can create or modify messages. They have also had their
            JWT token processed by middleware into request.user
        """

        results = {'status': 0}

        if not request.user.is_staff and not request.user.is_superuser:
            results['errors'] = 'Insufficient permissions'
            return JsonResponse(results, status=status.HTTP_403_FORBIDDEN)

        # if an id is passed, assume you are modifying a message, otherwise creating a new one
        if mid:
            try:
                message = Message.objects.get(id=mid)
            except ObjectDoesNotExist:
                results['errors'] = "Message %s not found" %mid
                return JsonResponse(results, status=status.HTTP_404_NOT_FOUND)

            serializer = MessageSerializer(message, data=request.POST, partial=True)
            stat = status.HTTP_200_OK

        else:
            serializer = MessageSerializer(data=request.POST, partial=False)
            stat = status.HTTP_201_CREATED

        if serializer.is_valid():
            serializer.save()
            results['data'] = serializer.data
            results['count'] = 1
            results['status'] = 1
            return JsonResponse(results, status=stat)

        results['errors'] = serializer.errors
        return JsonResponse(results, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, mid=None):
        """ a staff member or admin can delete messages """

        results = {'status': 0}

        if not request.user.is_staff and not request.user.is_superuser:
            results['errors'] = 'Insufficient permissions'
            return JsonResponse(results, status=status.HTTP_403_FORBIDDEN)

        if not mid:
            results['errors'] = 'Deleting message requires an id'
            return JsonResponse(results, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = Message.objects.get(id=mid)
        except ObjectDoesNotExist:
            results['errors'] = "Message %s not found" %mid
            return JsonResponse(results, status=status.HTTP_404_NOT_FOUND)
        try:
            message.delete()
            results['status'] = 1
        except Exception as exc:
            results['errors'] = str(exc)
            return JsonResponse(results, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(results, status=status.HTTP_200_OK)
