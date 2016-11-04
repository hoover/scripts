from datetime import datetime, timezone
from pathlib import Path
import json

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

class Document:
    def __init__(self, path, timestamp):
        self.path = path
        self.id = path.stem
        self.timestamp = timestamp

    def summary(self):
        return {
            'id': self.id,
            'updated': self.timestamp.isoformat(),
        }

def _now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)

def write_index(index_file, prev, chunk):
    data = {'documents': [
        doc.summary()
        for doc in (Document(i, _now()) for i in chunk)
    ]}
    if prev:
        data['next'] = str(prev)
    with index_file.open('w', encoding='utf-8') as f:
        json.dump(data, f, sort_keys=True, indent=2)

def main(repo):
    mofs = repo / 'mofs'
    indexdir = repo / 'index'
    filename = lambda n: indexdir / '{}.json'.format(n)
    for i, chunk in enumerate(chunked(sorted(mofs.iterdir())), 1):
        prev = filename(i - 1).relative_to(index.parent) if i > 1 else None
        index = filename(i)
        write_index(index, prev, chunk)

if __name__ == '__main__':
    import sys
    main(Path(sys.argv[1]))
