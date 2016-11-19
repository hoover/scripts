from urllib.request import urlopen
from urllib.parse import urljoin
import json

def get(url):
    f = urlopen(url)
    try:
        return json.loads(f.read().decode('utf8'))
    finally:
        f.close()

def docs(feed_url):
    while True:
        resp = get(feed_url)
        yield from resp['documents']

        next_url = resp.get('next')
        if next_url:
            feed_url = urljoin(feed_url, next_url)
        else:
            break

def cat_collection(collection_url):
    collection = get(collection_url)
    feed_url = urljoin(collection_url, collection['feed'])
    return docs(feed_url)

if __name__ == '__main__':
    import sys
    for doc in cat_collection(sys.argv[1]):
        print(json.dumps(doc))
