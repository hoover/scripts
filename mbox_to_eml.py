import sys
import re
from hashlib import sha1
from pathlib import Path

BUFSIZE = 1024 * 1024 # 1MB

def slice(stream):
    last = b''
    while True:
        buffer = stream.read(BUFSIZE)
        if not buffer:
            break
        window = last + buffer
        while True:
            m = re.search(br'\n\r\n(From )', window)
            if not m:
                break
            offset = m.start(1)
            yield window[:offset]
            window = window[offset:]
        last = window
    yield last

def unpack(mbox_path, out_path):
    with mbox_path.open('rb') as f:
        for n, message in enumerate(slice(f), 1):
            hash = sha1(str(n).encode('utf-8')).hexdigest()
            eml_path = out_path / hash[:2] / '{}.eml'.format(hash)
            eml_path.parent.mkdir(parents=True, exist_ok=True)
            with eml_path.open('wb') as f:
                f.write(message)
                print(n, hash, len(message))

if __name__ == '__main__':
    [mbox_arg, out_arg] = sys.argv[1:]
    unpack(Path(mbox_arg), Path(out_arg))
