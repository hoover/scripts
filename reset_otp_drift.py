# run from search repo, ./manage.py shell
from django.contrib.auth.models import User
stefan = User.objects.get(username='stefan')
[token] = stefan.totpdevice_set.all()
print('drift was', token.drift)
token.drift = 0
token.save()
