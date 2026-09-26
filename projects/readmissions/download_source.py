"""Download the pinned CMS release; never silently accept different source bytes."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'source.json').read_text(encoding='utf-8'))
    target = ROOT / 'data/hrrp.csv'
    if target.exists():
        data = target.read_bytes()
    else:
        request = urllib.request.Request(manifest['download_url'], headers={'User-Agent': 'Portfolio reproducibility download'})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
    if hashlib.sha256(data).hexdigest() != manifest['sha256']:
        raise ValueError('Source checksum changed. Review the release; do not overwrite the pinned manifest automatically.')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f'Verified CMS source: {len(data):,} bytes')


if __name__ == '__main__':
    main()
