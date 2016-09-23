# run from search repo, ./manage.py shell
from time import time
from django.contrib.auth.models import User
from django_otp.oath import TOTP

def get_token(username):
    return User.objects.get(username=username).totpdevice_set.get(confirmed=True)

def code(username, time, offset=0):
    token = get_token(username)
    totp = TOTP(
        token.bin_key,
        token.step,
        token.t0,
        token.digits,
        token.drift+offset,
    )
    totp.time = time
    return totp.token()

def codeset(username, time, tolerance):
    for offset in range(-tolerance, tolerance+1):
        print(offset, code(username, time, offset))
