# example-drf-jwt


The most critical decision I made was to get most the JWT functionality from the
Django Rest Framework Simple JWT (djangorestframework-simplejwt). After installing this,
I set it as default authentication in settings.py.

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        ...
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

When a person logs in, their token is returned, and this token must be put in the headers of all
subsequent requests. All the message APIs require authentication.

A sample login:

curl -X POST -d "username=test1&password=takehome4fracta" http://127.0.0.1:8000/login/

Returns:

{
  "status": 1,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjA3MjA4MDkxLCJqdGkiOiI1ZDE2YTdlZTU5MDE0NTRkYTNiZjA1OGQ4Y2ExZjdkYiJ9.gUAzG6KIGX3ywggctmw68YmNBW7abEb4eHc7WuH-zKk"
}

A sample call to the message endpoint puts that token in the headers:

curl -X GET -H "Authorization: Bearer $TOKEN"  http://127.0.0.1:8000/bus/messages/

Returns:
{
  "status": 1,
  "count": 1,
  "data": [{
    "id": 5,
    "user": 1,
    "message": "This is a  message to the admin"
  }]
}


Since the JWT is handled by middleware, the authentication takes place before the view is called,
and request.user can be assumed by the view to be verified from the header token.

I also allowed the message endpoint to take a different token, and display that other person's
messages, but only if the authenticated user is staff or superuser.

curl -X GET -H "Authorization: Bearer $TOKEN"  http://127.0.0.1:8000/bus/messages/?token={test1token}
{
  "status": 1,
  "count": 3,
  "data": [{
    "id": 1,
    "user": 2,
    "message": "This is a message just for test1"
  }, {
    "id": 3,
    "user": 2,
    "message": "This is another message just for test1"
  }, {
    "id": 4,
    "user": 2,
    "message": "There are many messages for test1"
  }]
}

I'm returning some other fields that were useful to the frontend at my current job.
Status is 0 for failure and 1 for success. Errors are put in "errors". The count of objects is
returned.
