""" tests for message_bus """
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework.test import APIRequestFactory

from message_bus.models import Message
from message_bus.views import Messages, JWTLogin


# Create your tests here.

class MessageTestCase(TestCase):
    """ tests for messages and JWT authorization """

    def setUp(self):
        """ create some users and a message for test data """

        hashpw = make_password('takehome4fracta')

        staff = User.objects.create(username='staff', password=hashpw, email='admin@forfracta.com',\
                                    is_active=1, is_staff=1, is_superuser=0)
        self.assertTrue(staff.is_staff)

        test1 = User.objects.create(username='test1', password=hashpw, email='test1@forfracta.com',\
                                    is_active=1, is_staff=0, is_superuser=0)

        self.assertTrue(test1.is_active)

        test2 = User.objects.create(username='test2', password=hashpw, email='test2@forfracta.com',\
                                    is_active=1, is_staff=0, is_superuser=0)
        self.assertIsNotNone(test2)

        test3 = User.objects.create(username='test3', password=hashpw, email='test3@forfracta.com',\
                                    is_active=1, is_staff=0, is_superuser=1)
        self.assertIsNotNone(test3)

        Message.objects.create(user=test1, message='This is a message only for test1')
        Message.objects.create(user=test2, message='This is a message only for test2')
        Message.objects.create(user=staff, message='This is a message only for staff')

        users = User.objects.all()
        self.assertEqual(len(users), 4)

        messages = Message.objects.all()
        self.assertEqual(len(messages), 3)


    def test_jwt_auth(self):
        """ test regular user login and access protected view """

        print('Logging in as test1')
        factory = APIRequestFactory()
        data = {"username": "test1", "password": "takehome4fracta"}

        request = factory.post('/login/', data)

        # have to manually add the session for login to work
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        view = JWTLogin.as_view()

        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

        content = json.loads(response.content.decode())
        if 'token' in content and content['token']:
            t1tok = content['token']
        else:
            t1tok = None

        self.assertIsNotNone(t1tok)

        print('Test1 makes a protected call for messages')
        request = factory.get('/bus/messages/', HTTP_AUTHORIZATION='Bearer {}'.format(t1tok),
                              content_type='application/json')

        view = Messages.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

        content = str(response.content)

        # should contain only the message for test1
        self.assertTrue(bool(content.find('test1') > -1))
        self.assertEqual(content.find('test2'), -1)


    def test_jwt_auth_staff(self):
        """ test staff login and access accessing protected view with other's token """

        print('Get test1 token')

        factory = APIRequestFactory()
        data = {"username": "test1", "password": "takehome4fracta"}

        request = factory.post('/login/', data)

        # have to manually add the session for login to work
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        view = JWTLogin.as_view()

        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

        content = json.loads(response.content.decode())
        if 'token' in content and content['token']:
            t1tok = content['token']
        else:
            t1tok = None

        self.assertIsNotNone(t1tok)

        print('\nLogging in as staff')

        factory = APIRequestFactory()
        data = {"username": "staff", "password": "takehome4fracta"}
        request = factory.post('/login/', data)

        middleware.process_request(request)
        request.session.save()

        view = JWTLogin.as_view()

        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

        content = json.loads(response.content.decode())
        if 'token' in content and content['token']:
            token = content['token']
        else:
            token = None

        print('Staff makes a protected call for messages for themselves')
        request = factory.get('/bus/messages/', HTTP_AUTHORIZATION='Bearer {}'.format(token),
                              content_type='application/json')

        view = Messages.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        content = str(response.content)

        # should contain only the message for staff
        self.assertTrue(bool(content.find('staff') > -1))
        self.assertEqual(content.find('test'), -1)

        print('Staff makes a protected call for messages with test1 token')
        request = factory.get('/bus/messages/?token='+t1tok,
                              HTTP_AUTHORIZATION='Bearer {}'.format(token),
                              content_type='application/json')

        view = Messages.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

        content = str(response.content)
       # should contain only the message for test1, not for staff
        self.assertTrue(bool(content.find('test1') > -1))
        self.assertEqual(content.find('staff'), -1)



    def test_message(self):
        """ Testing message api calls as staff """

        test3 = User.objects.get(username='test3')
        self.assertIsNotNone(test3)

        print('\nLogging in as staff')

        factory = APIRequestFactory()
        data = {"username": "staff", "password": "takehome4fracta"}
        request = factory.post('/login/', data)

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        view = JWTLogin.as_view()

        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

        content = json.loads(response.content.decode())
        if 'token' in content and content['token']:
            token = content['token']
        else:
            token = None

        self.assertIsNotNone(token)

        print('Staff makes a protected call creating a message')
        data = {"user": test3.id, "message": "this is a message just for test3"}

        request = factory.post('/bus/messages/', data, HTTP_AUTHORIZATION='Bearer {}'.format(token))

        view = Messages.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.content)

        content = json.loads(response.content.decode())
        if 'data' in content and 'id' in content['data']:
            mid = content['data']['id']
        else:
            mid = None

        self.assertIsNotNone(response.content)
        self.assertIsNotNone(mid)

        print('Staff makes a protected call modifying a message')

        data = {"message": "changing the message for test3"}

        request = factory.post('/bus/messages/', data, HTTP_AUTHORIZATION='Bearer {}'.format(token))
        response = view(request, mid)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

        content = json.loads(response.content.decode())
        if 'data' in content and 'message' in content['data']:
            mess = content['data']['message']
        else:
            mess = ''

        self.assertEqual(mess, "changing the message for test3")

        print('Staff makes a protected call deleting a message')

        request = factory.delete('/bus/messages/', HTTP_AUTHORIZATION='Bearer {}'.format(token))
        response = view(request, mid)

        self.assertEqual(response.status_code, 200)
