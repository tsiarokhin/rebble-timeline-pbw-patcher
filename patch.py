import os
import tempfile
import zipfile
import argparse
import glob
from urllib.parse import urlparse


def patch_js(app_js):
    return app_js.replace(b'timeline-api.getpebble.com', bytes(new_timeline_url, encoding='utf-8'))


def patch_pbw(original_pbw_path):
    tmp_fd, patched_pbw_path = tempfile.mkstemp()
    os.close(tmp_fd)

    with zipfile.ZipFile(original_pbw_path, 'r') as original_pbw:
        with zipfile.ZipFile(patched_pbw_path, 'w') as patched_pbw:
            for item in original_pbw.infolist():
                if item.filename != 'pebble-js-app.js':
                    patched_pbw.writestr(item, original_pbw.read(item.filename))
                else:
                    patched_pbw.writestr(item, patch_js(original_pbw.read(item.filename)))
    if args.output:
        os.rename(patched_pbw_path, os.path.join(args.output, os.path.basename(original_pbw_path)))
    else:
        os.remove(original_pbw_path)
        os.rename(patched_pbw_path, original_pbw_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patches pebble apps for use with another timeline API url.')
    parser.add_argument('path', help='path to .pbw or a directory of .pbw (non-recursive).')
    parser.add_argument('-u', '--url',
                        help='new timeline api url (default: timeline-api.rebble.io)',
                        type=str,
                        default='timeline-api.rebble.io')
    parser.add_argument('-o', '--output',
                        help='output directory for patched .pbw (default: replaces original .pbw)',
                        type=str)
    args = parser.parse_args()

    if '//' not in args.url:
        new_timeline_url = args.url
    else:
        new_timeline_url = urlparse(args.url).netloc

    if args.output is not None:
        os.makedirs(args.output)

    if os.path.isfile(args.path):
        patch_pbw(args.path)
        print('App successfully patched.')
    elif os.path.isdir(args.path):
        count = 0
        for pbw in glob.glob(args.path + '/*.pbw'):
            patch_pbw(pbw)
            count += 1
        print(count, 'apps successfully patched.')
    else:
        print('File or directory does not exists:', args.path)

