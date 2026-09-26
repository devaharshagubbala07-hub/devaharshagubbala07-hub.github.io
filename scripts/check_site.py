"""Check static pages, assets, anchors, JSON and JavaScript without dependencies.

Run from any directory: python scripts/check_site.py
Node.js is required for JavaScript syntax checks.
"""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE_HOST = 'devaharshagubbala07-hub.github.io'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = []
        self.links = []
        self.inline_json = []
        self.json_parts = None
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.links.append(attrs[key])
        if attrs.get('srcset'):
            self.links.extend(part.strip().split()[0] for part in attrs['srcset'].split(','))
        if tag == 'script' and attrs.get('type') in ('application/json', 'application/ld+json'):
            self.json_parts = []

    def handle_data(self, value):
        if self.json_parts is not None:
            self.json_parts.append(value)

    def handle_endtag(self, tag):
        if tag == 'script' and self.json_parts is not None:
            self.inline_json.append(''.join(self.json_parts))
            self.json_parts = None


def main():
    files = [p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts]
    pages = {p: Page(p) for p in files if p.suffix == '.html'}
    failures = []
    references = 0
    external = set()

    def check_link(source, value):
        nonlocal references
        url = urlsplit(value)
        if url.scheme in ('mailto', 'tel', 'data'):
            return
        if url.netloc and url.netloc != SITE_HOST:
            external.add(value)
            return
        references += 1
        path = unquote(url.path)
        target = ((ROOT / path.lstrip('/')) if path.startswith('/') or url.netloc else (source.parent / path)).resolve() if path else source
        if not target.is_relative_to(ROOT):
            failures.append(f'{source.relative_to(ROOT)}: path outside site: {value}')
            return
        if target.is_dir():
            target /= 'index.html'
        if not target.is_file():
            failures.append(f'{source.relative_to(ROOT)}: missing {value}')
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            failures.append(f'{source.relative_to(ROOT)}: missing anchor {value}')

    for path, page in pages.items():
        for id_, count in Counter(page.ids).items():
            if count > 1:
                failures.append(f'{path.relative_to(ROOT)}: duplicate ID {id_}')
        for value in page.links:
            check_link(path, value)
        for value in page.inline_json:
            try:
                json.loads(value)
            except ValueError as error:
                failures.append(f'{path.relative_to(ROOT)}: invalid inline JSON: {error}')

    for path in files:
        if path.suffix == '.css':
            for value in re.findall(r'url\([\'\"]?([^\)\'\"]+)', path.read_text(encoding='utf-8')):
                check_link(path, value)
        elif path.suffix == '.json':
            try:
                json.loads(path.read_text(encoding='utf-8'))
            except ValueError as error:
                failures.append(f'{path.relative_to(ROOT)}: invalid JSON: {error}')
        elif path.suffix == '.js':
            for value in re.findall(r'fetch\([\'\"]([^\'\"]+)', path.read_text(encoding='utf-8')):
                # Current dashboards load relative to their neighboring index.html.
                check_link(path.with_name('index.html'), value)
            node = shutil.which('node')
            if node:
                result = subprocess.run([node, '--check', str(path)], capture_output=True, text=True)
                if result.returncode:
                    failures.append(result.stderr.strip())
            else:
                failures.append('Node.js unavailable; JavaScript syntax was not checked.')

    if failures:
        print('\n'.join(failures))
        raise SystemExit(1)
    print(f'PASS: {len(pages)} pages, {references} local references, all JSON and JavaScript syntax.')
    print(f'{len(external)} distinct external links require a separate online check.')


if __name__ == '__main__':
    main()
