import sys
import json
import re
import django
django.setup()

from django.conf import settings
from snoop.models import Digest

def iter_rows(queryset, batch=10000):
    page = 0
    while True:
        start = batch * page
        end = start + batch
        rows = list(queryset.order_by('id')[start:end])
        if not rows:
            break
        yield from rows
        page += 1

for n, doc in enumerate(iter_rows(Digest.objects.all())):
    text = json.loads(doc.data).get('text', '')
    print('\n'.join(re.findall(r'\w+', text)))
    if not n % 100:
        print(n, file=sys.stderr)
