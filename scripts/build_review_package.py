"""Package active code and reviewed artifacts, excluding raw data and build caches.

This is a review package, never a claim that scientific/submission gates passed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TREES = ('src/', 'scripts/', 'tests/', 'docs/', 'notebooks/', 'results/sos/',
         'results/physical/', 'results/dartis/', 'results/qposd/', 'deliverables/report/',
         'deliverables/presentation/', 'deliverables/video/')
ROOT_FILES = {'.gitignore', '.gitattributes', '.python-version', 'README.md',
              'requirements.txt', 'pyproject.toml', 'uv.lock', 'run_experiments.py',
              'data/README.md', 'deliverables/README.md'}
META_FILES = ('data/manifest.json', 'data/dartis/catalog_manifest.json',
              'data/dartis/catalog.tsv')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def collect():
    names = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others',
                                     '--exclude-standard'], cwd=ROOT).decode('utf-8').split('\0')
    selected = set()
    for name in names:
        if not name or not (ROOT / name).is_file():
            continue
        if name in ROOT_FILES or name.startswith(TREES) or ('/' not in name and name.endswith('_12_11.docx')):
            selected.add(name)
    selected.update(name for name in META_FILES if (ROOT / name).is_file())
    # Keep the latest reviewed deliverables; historical versions remain in Git.
    selected.discard('deliverables/presentation/SAR_SOS_review_v1.pptx')
    selected.discard('deliverables/presentation/SAR_SOS_review_v2.pptx')
    selected.discard('deliverables/presentation/SAR_SOS_review_v3.pptx')
    selected.discard('deliverables/presentation/SAR_SOS_review_v4.pptx')
    selected.discard('deliverables/report/Bao_cao_SAR_SOS_review_v8.docx')
    selected.discard('deliverables/report/Bao_cao_SAR_SOS_review_v8.pdf')
    selected.discard('deliverables/report/Bao_cao_SAR_SOS_review_v9.docx')
    selected.discard('deliverables/report/Bao_cao_SAR_SOS_review_v9.pdf')
    selected.discard('deliverables/report/Bao_cao_SAR_SOS_review_v10.docx')
    selected.discard('deliverables/report/Bao_cao_SAR_SOS_review_v10.pdf')
    for name in selected:
        parts = Path(name).parts
        if any(p in {'.git', '.cache', '__pycache__', '.venv', 'legacy'} for p in parts):
            raise ValueError(f'Excluded directory entered package: {name}')
    return sorted(selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'deliverables/packages/SAR_review_v1.zip')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Choose a new output name; existing packages are not overwritten')
    audit_paths = ['docs/report/render_progress.json', 'docs/management/slides_audit.json',
                   'docs/management/video_audit.json', 'docs/management/video_visual_review.json']
    audits = [json.loads((ROOT / name).read_text(encoding='utf-8')) for name in audit_paths]
    report, slides, video, visual = audits
    expected = {
        'deliverables/report/Bao_cao_SAR_SOS_review_v11.docx': report['docx_sha256'],
        'deliverables/report/Bao_cao_SAR_SOS_review_v11.pdf': report['pdf_sha256'],
        slides['file']: slides['sha256'],
        'deliverables/video/SAR_demo_v1.mp4': video['sha256'],
    }
    assert report['all_pages_covered'] and report['layout_verified']
    assert video['full_decode_passed'] and visual['passed'] and visual['video_sha256'] == video['sha256']
    names = collect()
    assert set(expected).issubset(names)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.building')
    if temporary.exists():
        raise SystemExit('A previous temporary package exists; inspect it before retrying')
    entries = []
    with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in names:
            raw = (ROOT / name).read_bytes()
            digest = sha(raw)
            if name in expected:
                assert digest == expected[name], f'Reviewed artifact changed: {name}'
            archive.writestr(name, raw)
            entries.append({'path': name, 'bytes': len(raw), 'sha256': digest})
        manifest = {'format': 'sar-review-package-v1', 'submission_ready': False,
                    'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
                    'contains_worktree_changes': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)),
                    'files': entries, 'exclusions': ['raw imagery', 'virtual environment', 'caches',
                    'legacy history', 'Git history', 'historical presentations v1/v2/v3/v4 and reports v8/v9/v10'],
                    'scope': 'Review materials and saved evidence. Does not include source imagery needed to rerun inference/training.',
                    'required_next_steps': 'Read docs/management/completion_audit.json and deliverables/README.md'}
        archive.writestr('PACKAGE_MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    # Fail if a running job modified anything during the snapshot.
    for entry in entries:
        assert sha((ROOT / entry['path']).read_bytes()) == entry['sha256'], entry['path']
    with zipfile.ZipFile(temporary) as archive:
        assert archive.testzip() is None
        for entry in entries:
            assert sha(archive.read(entry['path'])) == entry['sha256']
    temporary.rename(output)
    receipt = {'file': output.relative_to(ROOT).as_posix() if output.is_relative_to(ROOT) else str(output),
               'sha256': sha(output.read_bytes()), 'bytes': output.stat().st_size,
               'members': len(entries), 'zip_crc_and_sha256_verified': True,
               'submission_ready': False, 'isolated_execution_verified': False}
    output.with_suffix('.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
