"""Requirement-driven validation supplement; preserves the original winner."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import json
from pathlib import Path


from scripts._provenance import source_matches
from scripts._paths import resolve_path
from scripts.cantarell.cantarell_experiment_data import ROOT, load_manifest, sha, require_committed
from scripts.cantarell.train_cantarell import write, rank

PROTOCOL = ROOT/'docs/management/cantarell_required_filter_protocol_v1.json'
OUTPUT = ROOT/'results/cantarell/requirements_selection.json'


def choose(rows):
    eligible = [r for r in rows if r['eligible'] and r['branch']=='gamma0'
                and r['config']['threshold']['name']=='niblack'
                and r['config']['filter']['name']!='none']
    if not eligible:
        raise ValueError('No converged retained filtered-adaptive candidate; no additional selection')
    return min(eligible,key=rank)


def main():
    load_manifest(['scripts/cantarell/select_cantarell_required_filter.py','scripts/cantarell/train_cantarell.py'])
    require_committed(PROTOCOL)
    base = ROOT/'results/cantarell'
    if (base/'evaluation.json').exists() or (base/'test_outputs').exists():
        raise ValueError('Additional selection must precede all physical test scoring')
    validation = json.loads((base/'validation.json').read_text())
    original = json.loads((base/'selection.json').read_text())
    if not validation['complete'] or (not source_matches(base/'validation.json', original['validation_sha256'], sha(base/'validation.json'))):
        raise ValueError('Complete matching validation is required')
    winner = choose(validation['rows'])
    selected = {k:winner[k] for k in ['branch','config_id','config','model_id','model_config','model_file','model_sha256','metrics']}
    output = {'protocol_sha256':sha(PROTOCOL),'script_sha256':sha(Path(__file__)),
              'validation_sha256':sha(base/'validation.json'),'original_selection_sha256':sha(base/'selection.json'),
              'selected':selected,'test_accessed':False,
              'validation_f1_difference_from_original_primary':winner['metrics']['numpy']['f1']-original['winners']['primary']['metrics']['numpy']['f1'],
              'disclosure':json.loads(PROTOCOL.read_text())['disclosure']}
    write(OUTPUT,output)
    print(json.dumps(output,indent=2))


if __name__=='__main__':
    main()
