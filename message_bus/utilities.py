""" This module contains little worker functions """
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError

from bus.settings import SIMPLE_JWT


def decode_token(token):
    """ little function to decode a token """

    tbe = TokenBackend(SIMPLE_JWT['ALGORITHM'])

    try:

        decoded = tbe.decode(token, False)

    except TokenBackendError:

        return 0

    return decoded


def token_user(token):
    """ get the user id from the token """

    decoded = decode_token(token)

    if decoded and 'user_id' in decoded:

        return int(decoded['user_id'])

    return 0
