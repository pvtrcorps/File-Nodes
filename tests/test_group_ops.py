import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

# Minimal fake bpy
_bpy = pytypes.ModuleType('bpy')
call_log = []

def _group_make():
    call_log.append('make')

def _group_ungroup():
    call_log.append('ungroup')

_bpy.ops = pytypes.SimpleNamespace(node=pytypes.SimpleNamespace(
    group_make=_group_make,
    group_ungroup=_group_ungroup,
))
_bpy.utils = pytypes.SimpleNamespace(register_class=lambda c: None, unregister_class=lambda c: None)
_bpy.types = pytypes.SimpleNamespace(Operator=object)
_bpy.data = pytypes.SimpleNamespace(node_groups=[])

sys.modules['bpy'] = _bpy
sys.modules['bpy.types'] = _bpy.types

spec_ops = importlib.util.spec_from_file_location('addon.operators', Path('operators.py'))
ops_mod = importlib.util.module_from_spec(spec_ops)
ops_mod.__package__ = 'addon'
exec(spec_ops.loader.get_code('addon.operators'), ops_mod.__dict__)
sys.modules['addon.operators'] = ops_mod

class GroupOpsTest(unittest.TestCase):
    def test_ops_call_blender(self):
        ops_mod.FN_OT_group_nodes().execute(None)
        ops_mod.FN_OT_ungroup_nodes().execute(None)
        self.assertEqual(call_log, ['make', 'ungroup'])

if __name__ == '__main__':
    unittest.main()
