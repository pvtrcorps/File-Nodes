import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

# Create fake bpy module
_bpy = pytypes.ModuleType('bpy')

class _OpsWM:
    call_count = 0

    @staticmethod
    def alembic_import(filepath=""):
        _OpsWM.call_count += 1
        obj = pytypes.SimpleNamespace(
            name=f"Obj{_OpsWM.call_count}", data=pytypes.SimpleNamespace()
        )
        _context.scene.objects.append(obj)

_bpy.ops = pytypes.SimpleNamespace(wm=_OpsWM)

class _Path:
    @staticmethod
    def abspath(path):
        return path

_bpy.path = _Path()

class _Types:
    Node = object

_bpy.types = _Types()
_bpy.data = pytypes.SimpleNamespace()
_bpy.__path__ = []
sys.modules['bpy.types'] = _bpy.types

sys.modules['bpy'] = _bpy

# Fake context and modifier helpers
class DummyMod:
    def __init__(self):
        self.created = []
        self.links = []
    def remember_object_link(self, collection, obj):
        self.links.append((collection, obj))
    def remember_created_id(self, data):
        self.created.append(data)

def dummy_mod():
    return DummyMod()

def setup_module(module):
    global _context
    _context = pytypes.SimpleNamespace()
    _context.scene = pytypes.SimpleNamespace(objects=[], collection=[])


class AlembicCacheTest(unittest.TestCase):
    def test_alembic_cached(self):
        spec = importlib.util.spec_from_file_location(
            'nodes.import_alembic', Path('nodes/import_alembic.py'),
            submodule_search_locations=['nodes']
        )
        ia = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ia)
        ia.get_active_mod_item = dummy_mod
        node = ia.FNImportAlembic.__new__(ia.FNImportAlembic)
        out1 = ia.FNImportAlembic.process(node, _context, {"File Path": "some.abc"})
        out2 = ia.FNImportAlembic.process(node, _context, {"File Path": "some.abc"})
        self.assertEqual(_Bpy.ops.wm.call_count, 1)
        self.assertEqual(out1, out2)
        self.assertEqual(len(out1["Objects"]), 1)


if __name__ == "__main__":
    unittest.main()
