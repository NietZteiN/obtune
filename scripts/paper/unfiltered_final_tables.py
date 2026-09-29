"""Regenerate final-paper Tables 6, 8 and 9 from all cells, without a format gate.

Uses the phase precedence and equal-condition means of 59_master_tables.py;
backward scores prefer the corrected v2 execution grade. Table 7 is generated
separately by 76_merge_ablation.py --unfiltered. Missing cells are fatal.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
CELLS = ROOT / 'results/cells'
MODELS = ['codellama-7b', 'codellama-13b', 'codellama-34b', 'llama31-8b',
          'starcoder2-15b', 'gemma3-12b', 'codegemma-7b', 'granite31-8b']
ARMS = ['base', 'tuned_L0', 'mono_all', 'cons_lam3', 'mole_router', 'merge_dare_ties']
SINGLES = ['L1b', 'L1r', 'L2', 'S1', 'S2']
D2 = ['C_L1b_S1', 'C_L1r_S1', 'C_S1_L1r', 'C_L2_S4', 'C_L1r_S3', 'C_S4_S3']
D3 = ['C3_L1r_S3_S4', 'C3_S1_S3_S4', 'C3_L1r_S1_S4']
D4 = ['C4_L1r_S1_S3_S4']
UNSEEN = ['X1', 'C_L1r_X1', 'C_X1_S1', 'C_S2_X1', 'C_L1r_X1m', 'C_S1_X1s', 'C3_L1r_S1_X1']
REVERSE = ['L0'] + SINGLES + D2 + D3 + D4 + UNSEEN
FALLBACK = ['merge_panel', 'mole_generic', 'rq2_generic', 'panel_core',
            'composite_generic', 'composite_depth', 'f2_divergence']
SOURCES = {}


def score(model, arm, cond, backward=False):
    if backward:
        phases = ['inverse_1shot', 'inverse_generic']
    elif arm == 'mole_router':
        phases = ['mole_generic']
    elif arm == 'merge_dare_ties':
        phases = ['merge_panel', 'rq2_generic', 'composite_generic', 'f2_divergence']
    else:
        phases = (['panel_core'] if cond in ['L0'] + SINGLES + ['X1'] else
                  ['composite_generic'] if cond in D2 else
                  ['composite_depth', 'composite_generic'] if cond in D3 + D4 else
                  ['f2_divergence']) + FALLBACK
    for phase in phases:
        folder = CELLS / phase / model / 'python' / f'{arm}__{cond}'
        path = folder / 'cell_meta_v2.json'
        if not path.exists():
            path = folder / 'cell_meta.json'
        if path.exists():
            data = json.loads(path.read_text())
            value = data.get('accuracy')
            if value is not None:
                assert 0 <= value <= 1, path
                SOURCES[str(path.relative_to(ROOT))] = {
                    'accuracy': value, 'format_fail_rate': data.get('format_fail_rate'),
                    'git_commit': data.get('git_commit'), 'run_id': data.get('run_id')}
                return value
    raise FileNotFoundError(f'{model}/{arm}/{cond}, backward={backward}')


def mean(model, arm, conditions, backward=False):
    return sum(score(model, arm, cond, backward) for cond in conditions) / len(conditions)


def display(value, base=None, bold=False, delta=False):
    text = f'{value:+.1f}' if delta else f'{value:.3f}'.removeprefix('0')
    # Colour the displayed comparison; avoid red/green for a rounded tie.
    if base is not None and round(value, 3) != round(base, 3):
        colour = 'green!55!black' if value > base else 'red!70!black'
        text = r'\textcolor{' + colour + '}{' + text + '}'
    return r'\textbf{' + text + '}' if bold else text


def update_table(table, number):
    groups = ([('Clean', ['L0'], False), ('Singles', SINGLES, False)] if number == 6 else
              [('2', D2, False), ('3', D3, False), ('4', D4, False)] if number == 8 else
              [('Held-out', UNSEEN, False), ('Reverse', REVERSE, True)])
    expected = 10 if number == 8 else 8
    start = table.index(r'\midrule')
    prefix, body = table[:start], table[start:]
    row_index = 0
    records = []

    def replace(match):
        nonlocal row_index
        row = match.group()
        cells = row[:-2].split('&')
        if len(cells) != expected:
            return row
        model = MODELS[row_index // len(groups)]
        label, conditions, backward = groups[row_index % len(groups)]
        values = [mean(model, arm, conditions, backward) for arm in ARMS]
        best = max(round(v, 3) for v in values[1:])
        numbers = [display(values[0])] + [
            display(v, values[0], round(v, 3) == best) for v in values[1:]]
        records.append({'model': model, 'group': label, 'conditions': conditions,
                        'backward': backward, 'accuracy': dict(zip(ARMS, values))})
        if number == 8:
            reference = score(model, 'base', 'L0')
            if row_index % 3 == 0:
                cells[1] = ' ' + display(reference) + '\n'
            indices = range(3, 9)
            cells[9] = ' ' + display((values[-1] - reference) * 100, 0, delta=True) + ' '
        else:
            indices = range(2, 8)
        for index, value in zip(indices, numbers):
            cells[index] = ' ' + value + (' ' if index == expected - 1 else '\n')
        row_index += 1
        return '&'.join(cells) + r'\\'

    body = re.sub(r'(?:(?!\\\\)[\s\S])*?\\\\', replace, body)
    assert row_index == len(MODELS) * len(groups), (number, row_index)
    # Make the scope of the unfiltered means explicit.
    note = '% All evaluated cells included; no format-failure gate.\n'
    if note not in prefix:
        prefix = prefix.replace(r'\label{', note + r'\label{', 1)
    return prefix + body, records


def main():
    path = ROOT / 'paper/final/sections/results.tex'
    source = path.read_text()
    records = {}
    counter = iter([6, 8, 9])
    def replace(match):
        number = next(counter)
        table, records[str(number)] = update_table(match.group(), number)
        return table
    updated = re.sub(r'\\begin\{table\*\}.*?\\end\{table\*\}', replace, source, flags=re.S)
    assert len(records) == 3
    path.write_text(updated)
    output = ROOT / 'results/analysis/pipeline/final_tables_unfiltered.json'
    output.write_text(json.dumps({'format_filter': False, 'aggregation': 'equal-condition mean',
                                 'tables': records, 'sources': SOURCES}, indent=2) + '\n')
    print(f'Updated Tables 6, 8 and 9 from {len(SOURCES)} source cells; wrote {output}')


if __name__ == '__main__':
    main()
