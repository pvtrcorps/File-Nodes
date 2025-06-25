import types as pytypes
import sys
import importlib.util
import unittest
from pathlib import Path

# Fake bpy module (reuse existing if created by other tests)
_bpy = sys.modules.get('bpy', pytypes.ModuleType('bpy'))

class _Scenes:
    call_count = 0
    def new(self, name=""):
        self.__class__.call_count += 1
        return pytypes.SimpleNamespace(name=f"{name}")

if not hasattr(_bpy, 'data'):
    _bpy.data = pytypes.SimpleNamespace(scenes=_Scenes())
else:
    _bpy.data.scenes = _Scenes()

class _Types:
    class Node:
        pass

_bpy.types = getattr(_bpy, 'types', _Types())
_bpy.__path__ = getattr(_bpy, '__path__', [])
sys.modules['bpy.types'] = _bpy.types
sys.modules['bpy'] = _bpy

# Fake addon package hierarchy
_addon = pytypes.ModuleType('addon')
_addon.__path__ = ['.']
sys.modules['addon'] = _addon
_nodes_pkg = pytypes.ModuleType('addon.nodes')
_nodes_pkg.__path__ = ['nodes']
sys.modules['addon.nodes'] = _nodes_pkg

_sockets = sys.modules.get('addon.sockets')
if not _sockets:
    _sockets = pytypes.ModuleType('addon.sockets')
    sys.modules['addon.sockets'] = _sockets
class FNSocketScene: pass
class FNSocketString: pass
_sockets.FNSocketScene = FNSocketScene
_sockets.FNSocketString = FNSocketString

_operators = pytypes.ModuleType('addon.operators')
def get_active_mod_item():
    return dummy_mod()
_operators.get_active_mod_item = get_active_mod_item
sys.modules['addon.operators'] = _operators

# Dummy modifier
class DummyMod:
    def __init__(self):
        self.created = []
        self.scenes = []
    def remember_created_scene(self, sc):
        self.scenes.append(sc)
    def remember_created_id(self, data):
        self.created.append(data)

def dummy_mod():
    return DummyMod()

def setup_module(module):
    global _context
    _context = pytypes.SimpleNamespace()

class NewSceneCacheTest(unittest.TestCase):
    def test_scene_cached(self):
        spec = importlib.util.spec_from_file_location(
            'addon.nodes.new_scene', Path('nodes/new_scene.py'),
            submodule_search_locations=['nodes']
        )
        ns = importlib.util.module_from_spec(spec)
        ns.__package__ = 'addon.nodes'
        code = Path('nodes/new_scene.py').read_text()
        exec(compile(code, 'nodes/new_scene.py', 'exec'), ns.__dict__)
        ns.get_active_mod_item = dummy_mod
        node = ns.FNNewScene.__new__(ns.FNNewScene)
        out1 = ns.FNNewScene.process(node, _context, {"Name": "Scene"})
        out2 = ns.FNNewScene.process(node, _context, {"Name": "Scene"})
        self.assertEqual(_bpy.data.scenes.call_count, 1)
        self.assertEqual(out1, out2)

if __name__ == "__main__":
    unittest.main()
