"""Requirement-driven validation supplement; preserves the original winner."""
import json
from pathlib import Path

from cantarell_experiment_data import ROOT, load_manifest, sha, require_committed
from train_cantarell import write, rank

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
    load_manifest(['scripts/select_cantarell_required_filter.py','scripts/train_cantarell.py'])
    require_committed(PROTOCOL)
    base = ROOT/'results/cantarell'
    if (base/'evaluation.json').exists() or (base/'test_outputs').exists():
        raise ValueError('Additional selection must precede all physical test scoring')
    validation = json.loads((base/'validation.json').read_text())
    original = json.loads((base/'selection.json').read_text())
    if not validation['complete'] or original['validation_sha256']!=sha(base/'validation.json'):
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
