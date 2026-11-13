"""Download all catalog no-oil JPEGs with bounded concurrency and resumable checks.

No training, image selection by outcome, or credentials required. Run audit_dartis
first to create the local catalog manifest. Reuse only decodable existing images.
"""
import argparse
import hashlib
import io
import json
import re
import time
import threading
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://download.pangaea.de/dataset/980773/files/'
RATE_LIMIT = ROOT / 'results/dartis/rate_limit.json'
STOP_NETWORK = threading.Event()
REQUEST_LOCK = threading.Lock()
NEXT_REQUEST = 0.0


def cooldown_seconds(header, now):
    """Honor Retry-After seconds/date; use 15 minutes if absent or invalid."""
    try:
        value = float(header)
    except (TypeError, ValueError):
        try:
            value = parsedate_to_datetime(header).timestamp() - now
        except (TypeError, ValueError, AttributeError, OverflowError):
            return 900.0
    return max(60.0, value)


def request_slot():
    """At most one new request per two seconds across download threads."""
    global NEXT_REQUEST
    if STOP_NETWORK.is_set():
        return False
    with REQUEST_LOCK:
        if STOP_NETWORK.is_set():
            return False
        delay = max(0.0, NEXT_REQUEST - time.monotonic())
        if delay:
            time.sleep(delay)
        NEXT_REQUEST = time.monotonic() + 2.0
        return not STOP_NETWORK.is_set()


def validate(raw, row):
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        if image.format != 'JPEG' or image.size != (row['width'], row['height']):
            raise ValueError('JPEG format or dimensions differ from catalog')
    return hashlib.sha256(raw).hexdigest()


def fetch(row):
    name = row['filename']
    if not re.fullmatch(r'n[cw]-[0-9-]+\.jpg', name):
        raise ValueError('Unexpected catalog filename: ' + name)
    dest = ROOT / 'data/dartis' / name
    if dest.exists():
        digest = validate(dest.read_bytes(), row)
        return {'filename': name, 'sha256': digest, 'bytes': dest.stat().st_size,
                'source': BASE + name, 'reused': True}
    error = None
    for attempt in range(3):
        if not request_slot():
            return {'filename': name, 'error': 'Deferred: publisher rate limit reached'}
        try:
            # Retry a transient CDN error through the same public download endpoint.
            url = BASE + name + (f'?download={attempt}' if attempt > 0 else '')
            request = urllib.request.Request(url, headers={'User-Agent': 'SAR-coursework-data-audit/1.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read(32 * 1024 * 1024 + 1)
            if len(raw) > 32 * 1024 * 1024:
                raise ValueError('Unexpected image larger than 32 MiB')
            digest = validate(raw, row)
            temp = dest.with_suffix('.download')
            temp.write_bytes(raw)
            temp.replace(dest)
            return {'filename': name, 'sha256': digest, 'bytes': len(raw),
                    'source': url, 'reused': False}
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                STOP_NETWORK.set()
                now = time.time()
                delay = cooldown_seconds(exc.headers.get('Retry-After'), now)
                RATE_LIMIT.parent.mkdir(parents=True, exist_ok=True)
                # All threads stop issuing new requests; retain the latest resume time.
                with REQUEST_LOCK:
                    prior = json.loads(RATE_LIMIT.read_text()) if RATE_LIMIT.exists() else {}
                    resume = max(prior.get('resume_not_before_unix', 0), now + delay)
                    RATE_LIMIT.write_text(json.dumps({'http_status':429, 'observed_unix':now,
                        'retry_after_header':exc.headers.get('Retry-After'),
                        'resume_not_before_unix':resume, 'source':url},indent=2)+'\n',encoding='utf-8')
                return {'filename':name, 'error':error, 'resume_not_before_unix':resume}
            if attempt < 2:
                time.sleep(attempt + 1)
    return {'filename': name, 'error': error}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=1, choices=range(1, 9))
    args = parser.parse_args()
    if RATE_LIMIT.exists():
        cooldown = json.loads(RATE_LIMIT.read_text())
        remaining = cooldown['resume_not_before_unix'] - time.time()
        if remaining > 0:
            raise SystemExit(f'Publisher rate limit: retry after at least {remaining:.0f} seconds')
    manifest = ROOT / 'data/dartis/catalog_manifest.json'
    rows = [r for r in json.loads(manifest.read_text(encoding='utf-8')) if r['subset'] in {'nc', 'nw'}]
    assert len({r['filename'] for r in rows}) == len(rows) == 2290
    output = ROOT / 'results/dartis'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    started = time.perf_counter()

    def save():
        errors = sum('error' in r for r in results)
        report = {'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
                  'expected': len(rows), 'completed': len(results), 'errors': errors,
                  'complete': len(results) == len(rows) and errors == 0,
                  'elapsed_seconds': time.perf_counter() - started,
                  'files': sorted(results, key=lambda r: r['filename'])}
        (output / 'download_audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(fetch, row) for row in rows]
        for job in as_completed(jobs):
            results.append(job.result())
            if len(results) % 25 == 0:
                save()
                print(f"{len(results)}/{len(rows)}; errors={sum('error' in r for r in results)}", flush=True)
    save()
    if any('error' in r for r in results):
        raise SystemExit('Incomplete download; see download_audit.json and retry')
    print(f'All {len(rows)} no-oil images decoded and hashed.', flush=True)


if __name__ == '__main__':
    main()
