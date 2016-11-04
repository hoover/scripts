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

def write_index(index_file, prev, chunk):
    timestamp = datetime.utcnow().replace(tzinfo=timezone.utc)
    data = {
        'timestamp': timestamp.isoformat(),
        'documents': {
            doc.id: doc.timestamp.isoformat()
            for doc in (Document(i, timestamp) for i in chunk)
        },
    }
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
