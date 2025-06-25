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
        class DummyObj:
            def __init__(self, name):
                self.name = name
                self.data = pytypes.SimpleNamespace()
            def __hash__(self):
                return hash(id(self))
        obj = DummyObj(f"Obj{_OpsWM.call_count}")
        _context.scene.objects.append(obj)

_bpy.ops = pytypes.SimpleNamespace(wm=_OpsWM)

class _Path:
    @staticmethod
    def abspath(path):
        return path

_bpy.path = _Path()

class _Types:
    class Node:
        pass

_bpy.types = _Types()
_bpy.data = pytypes.SimpleNamespace()
_bpy.__path__ = []
sys.modules['bpy.types'] = _bpy.types
sys.modules['bpy'] = _bpy

# Fake addon package hierarchy for relative imports
_addon = pytypes.ModuleType('addon')
_addon.__path__ = ['.']
sys.modules['addon'] = _addon
_nodes_pkg = pytypes.ModuleType('addon.nodes')
_nodes_pkg.__path__ = ['nodes']
sys.modules['addon.nodes'] = _nodes_pkg

_sockets = pytypes.ModuleType('addon.sockets')
class FNSocketObjectList: pass
class FNSocketString: pass
sys.modules['addon.sockets'] = _sockets
_sockets.FNSocketObjectList = FNSocketObjectList
_sockets.FNSocketString = FNSocketString

# Fake context helper

def setup_module(module):
    global _context
    _context = pytypes.SimpleNamespace()
    _context.scene = pytypes.SimpleNamespace(objects=[], collection=[])


class AlembicCacheTest(unittest.TestCase):
    def test_alembic_cached(self):
        spec = importlib.util.spec_from_file_location(
            'addon.nodes.import_alembic', Path('nodes/import_alembic.py'),
            submodule_search_locations=['nodes']
        )
        ia = importlib.util.module_from_spec(spec)
        ia.__package__ = 'addon.nodes'
        code = Path('nodes/import_alembic.py').read_text()
        exec(compile(code, 'nodes/import_alembic.py', 'exec'), ia.__dict__)
        node = ia.FNImportAlembic.__new__(ia.FNImportAlembic)
        node.id_data = pytypes.SimpleNamespace(fn_inputs=None)
        out1 = ia.FNImportAlembic.process(node, _context, {"File Path": "some.abc"})
        out2 = ia.FNImportAlembic.process(node, _context, {"File Path": "some.abc"})
        self.assertEqual(_bpy.ops.wm.call_count, 1)
        self.assertEqual(out1, out2)
        self.assertEqual(len(out1["Objects"]), 1)


if __name__ == "__main__":
    unittest.main()
