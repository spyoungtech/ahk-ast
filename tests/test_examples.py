import json
import os
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')))
from ahk_ast import model, parser

tests_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples'))


def load_spec(fp) -> model.Program:

    spec = spec_from_file_location(os.path.basename(fp).replace('.py', ''), fp)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.model


error_specs = []
specs = []

for root, dirs, files in os.walk(tests_path):
    for f in files:
        if f.endswith('.ahk'):
            specs.append(os.path.join(root, f))
        elif f.endswith('.invalid-ahk'):
            error_specs.append(os.path.join(root, f))


@pytest.mark.parametrize('fp', specs)
def test_official_files(fp):
    if not os.path.exists(tests_path):
        pytest.mark.skip('Tests repo was not present in expected location. Skipping.')
        return

    spec_file = fp.replace('.ahk', '_spec.py')
    if not os.path.exists(spec_file):
        raise Exception(f'Missing spec file, {spec_file}')

    expected = load_spec(spec_file)
    with open(fp) as f:
        text = f.read()
    actual = parser.parse(text)
    assert expected == actual, ''
