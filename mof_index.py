from datetime import datetime, timezone
from pathlib import Path
import re
import json
import subprocess

ID_PATTERN = r'^mof(?P<part>\d)_(?P<year>\d{4})_(?P<number>\d+)$'

def chunked(items, chunksize=100):
    iterator = iter(items)
    while True:
        buffer = []
        try:
            for _ in range(chunksize):
                buffer.append(next(iterator))
        except StopIteration:
            if not buffer:
                return
        yield buffer

def pdftotext(path):
    cmd = ['pdftotext', str(path), '-']
    return subprocess.check_output(cmd).decode('utf8')

class Document:
    def __init__(self, path, datadir):
        self.path = path
        self.version = None
        m = re.match(ID_PATTERN, path.stem)
        self.id_parts = dict(m.groupdict())
        self.id = 'mof{part}/{year}/{number}'.format(**self.id_parts)
        self.data_path = datadir / (self.id + '.json')
        if self.data_path.exists():
            with self.data_path.open('r', encoding='utf8') as f:
                data = json.load(f)
            self.version = data['version']

    def digest(self):
        self.version = _now()
        data = {
            'id': self.id,
            'version': self.version,
            'content': {
                'title': ("MOF partea {part}, nr {number} din {year}"
                    .format(**self.id_parts)),
                'text': pdftotext(self.path),
            },
        }
        self.data_path.parent.mkdir(exist_ok=True, parents=True)
        with self.data_path.open('w', encoding='utf8') as f:
            json.dump(data, f, sort_keys=True, indent=2)

    def summary(self):
        return {
            'id': self.id,
            'version': self.version,
        }

def _now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)

def write_feed(feed_file, prev, docs):
    data = {'documents': [doc.summary() for doc in docs]}
    if prev:
        data['next'] = str(prev)
    with feed_file.open('w', encoding='utf-8') as f:
        json.dump(data, f, sort_keys=True, indent=2)

def main(repo):
    mofs = repo / 'mofs'
    feeddir = repo / 'feed'
    datadir = repo / 'data'
    filename = lambda n: feeddir / '{}.json'.format(n)
    for i, chunk in enumerate(chunked(sorted(mofs.iterdir())), 1):
        docs = []
        for path in chunk:
            if path.suffix != '.pdf':
                continue
            doc = Document(path, datadir)
            if doc.version is None:
                doc.digest()
            docs.append(doc)
        prev = filename(i - 1).relative_to(feed.parent) if i > 1 else None
        feed = filename(i)
        write_feed(feed, prev, docs)

    latest = feeddir / 'latest.json'
    if latest.exists(): latest.unlink()
    latest.symlink_to(feed.relative_to(latest.parent))

if __name__ == '__main__':
    import sys
    main(Path(sys.argv[1]))
