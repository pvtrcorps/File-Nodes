import types as pytypes
import sys
import importlib.util
from pathlib import Path

_bpy = sys.modules.get('bpy', pytypes.ModuleType('bpy'))
if not hasattr(_bpy, 'types'):
    class _Types:
        class Node:
            pass
    _bpy.types = _Types()
_bpy.__path__ = getattr(_bpy, '__path__', [])
sys.modules['bpy.types'] = _bpy.types
sys.modules['bpy'] = _bpy

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
class FNSocketSceneList:
    pass
_sockets.FNSocketSceneList = FNSocketSceneList

spec = importlib.util.spec_from_file_location(
    'addon.nodes.output_nodes', Path('nodes/output_nodes.py'),
    submodule_search_locations=['nodes']
)
mod = importlib.util.module_from_spec(spec)
mod.__package__ = 'addon.nodes'
code = Path('nodes/output_nodes.py').read_text()
exec(compile(code, 'nodes/output_nodes.py', 'exec'), mod.__dict__)


class TestOutputScenes:
    def test_process_handles_unset_keep_list(self):
        node = mod.FNOutputScenesNode.__new__(mod.FNOutputScenesNode)
        node.id_data = pytypes.SimpleNamespace(
            fn_inputs=pytypes.SimpleNamespace(scenes_to_keep=None)
        )
        result = mod.FNOutputScenesNode.process(
            node, pytypes.SimpleNamespace(), {"Scenes": [1, None, 2]}
        )
        assert node.id_data.fn_inputs.scenes_to_keep == [1, 2]
        assert result == {}

