#!/usr/bin/env python3

from pathlib import Path
from tempfile import NamedTemporaryFile
import re
import json
from urllib.parse import parse_qs

def walk(root):
    hoover = root / '.hoover'
    hoover.mkdir(exist_ok=True)
    tmp = NamedTemporaryFile('wt', encoding='utf8',
        dir=str(hoover), delete=False)
    try:
        with tmp:
            for file in root.glob('**/*.html'):
                path = file.relative_to(root)
                mtime = file.stat().st_mtime
                print(path, mtime, file=tmp)
        Path(tmp.name).rename(hoover / 'index.txt')
    except:
        Path(tmp.name).unlink()
        raise

def _walk_subparser(commands):
    parser = commands.add_parser('walk')
    parser.set_defaults(handler=lambda root, options: walk(root))

walk.subparser = _walk_subparser

def touch_all(root):
    for file in root.glob('**/*.html'):
        file.touch()

def _touch_all_subparser(commands):
    parser = commands.add_parser('touch_all')
    parser.set_defaults(handler=lambda root, options: touch_all(root))

touch_all.subparser = _touch_all_subparser

def _index(root):
    with (root / '.hoover' / 'index.txt').open(encoding='utf8') as f:
        lines = (line.strip().split() for line in f)
        pairs = ((Path(p), t) for p, t in lines)
        return {
            p.stem: {
                'path': p,
                'version': v,
                'sort': '{}:{}'.format(int(float(v)), p.stem),
            }
            for p, v in pairs
        }

def _digest(id, path, version):
    with path.open(encoding='latin1') as f:
        html = f.read()
    text = ' '.join(re.sub(r'<[^>]*>', ' ', html).split())
    return {
        'id': id,
        'version': version,
        'content': {
            'title': path.stem,
            'text': text,
        },
        'views': [
            {'name': "html", 'url': str(path)},
        ],
    }

def digest(root, id):
    index = _index(root)
    doc = index[id]
    return _digest(id, root / doc['path'], doc['version'])

def _digest_subparser(commands):
    parser = commands.add_parser('digest')
    parser.add_argument('id')
    parser.set_defaults(handler=lambda root, options:
        print(digest(root, options.id)))

digest.subparser = _digest_subparser

def serve(root, listen):
    from wsgiref.simple_server import make_server
    (host, port) = listen.split(':')

    index = _index(root)
    sorted_ids = sorted(index, key=lambda i: index[i]['sort'], reverse=True)

    def json_response(environ, start_response, data):
        start_response('200 OK', [('Content-Type', 'application/json')])
        data = json.dumps(data, indent=2, sort_keys=True) + '\n'
        return [data.encode('utf8')]

    def meta_view(environ, start_response):
        return json_response(environ, start_response, {
            'name': "Luxembourg Companies",
            'feed': 'feed',
        })

    def feed_view(environ, start_response):
        lt = parse_qs(environ['QUERY_STRING']).get('lt', [None])[0]
        documents = []
        for id in sorted_ids:
            sort = index[id]['sort']
            if lt is None or sort < lt:
                path = index[id]['path']
                documents.append(_digest(id, root / path, index[id]['version']))
                if len(documents) >= 100:
                    break
        resp = {'documents': documents}
        if documents:
            resp['next'] = '?lt={}'.format(sort)
        return json_response(environ, start_response, resp)

    routes = [
        (r'/$', meta_view),
        (r'/feed$', feed_view),
    ]

    def wsgiapp(environ, start_response):
        for rule, handler in routes:
            match = re.match(rule, environ['PATH_INFO'])
            if match:
                return handler(environ, start_response, **match.groupdict())

        start_response('404 Not Found', [])
        return [b'noting here\n']

    httpd = make_server(host, int(port), wsgiapp)
    print('serving on', host, port)
    httpd.serve_forever()

def _serve_subparser(commands):
    parser = commands.add_parser('serve')
    parser.add_argument('listen')
    parser.set_defaults(handler=lambda root, options:
        serve(root, options.listen))

serve.subparser = _serve_subparser

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-d', '--data')
    commands = parser.add_subparsers()
    walk.subparser(commands)
    touch_all.subparser(commands)
    digest.subparser(commands)
    serve.subparser(commands)
    options = parser.parse_args()

    root = Path(options.data).resolve()
    options.handler(root, options)

if __name__ == '__main__':
    main()
