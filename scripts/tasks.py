"""Browse and run project tools without memorizing their file locations."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = json.loads((ROOT/'scripts/catalog.json').read_text(encoding='utf-8'))
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    listing = commands.add_parser('list', help='List tools; no script is executed')
    listing.add_argument('--group', choices=sorted({r['group'] for r in catalog}))
    run = commands.add_parser('run', help='Run one named tool, forwarding its arguments')
    run.add_argument('task', choices=[r['task'] for r in catalog])
    run.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.action == 'list':
        for row in catalog:
            if args.group is None or row['group'] == args.group:
                print(f"{row['task']:<52} {row['path']}")
        return 0
    row = next(r for r in catalog if r['task'] == args.task)
    path = ROOT/row['path']
    if not path.is_file() or not path.resolve().is_relative_to((ROOT/'scripts').resolve()):
        parser.error('Catalog target missing or outside scripts/')
    forwarded = args.arguments
    if forwarded[:1] == ['--']:
        forwarded = forwarded[1:]
    executable = {'.py': [sys.executable], '.mjs': ['node'],
                  '.ps1': ['powershell', '-NoProfile', '-File']}[path.suffix]
    return subprocess.call([*executable, str(path), *forwarded], cwd=ROOT)


if __name__ == '__main__':
    raise SystemExit(main())
