"""Node to replace a scene's view layers with a provided list."""

import bpy
from bpy.types import Node

from .base import FNBaseNode
from ..sockets import FNSocketScene, FNSocketViewLayerList


class FNSetSceneViewlayers(Node, FNBaseNode):
    """Replace the view layers in a scene."""

    bl_idname = "FNSetSceneViewlayers"
    bl_label = "Set Scene View Layers"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketScene', "Scene")
        sock = self.inputs.new('FNSocketViewLayerList', "ViewLayers")
        sock.display_shape = 'SQUARE'
        self.outputs.new('FNSocketScene', "Scene")

    def process(self, context, inputs, manager):
        scene = inputs.get("Scene")
        layers = [vl for vl in (inputs.get("ViewLayers") or []) if vl]
        if not scene:
            return {"Scene": scene}
        

        def _warn(msg):
            report = getattr(self, "report", None)
            if callable(report):
                report({'WARNING'}, msg)
            else:
                pass

        # Ensure all layers belong to the scene
        filtered = []
        names = []
        for layer in layers:
            owner = getattr(layer, "id_data", None)
            if owner is not scene:
                _warn(f"View layer '{getattr(layer, 'name', '')}' does not belong to scene '{scene.name}'")
                continue
            if layer.name in names:
                # Replace any previous layer with the same name
                idx = names.index(layer.name)
                filtered[idx] = layer
            else:
                names.append(layer.name)
                filtered.append(layer)

        # Reorder and remove layers according to filtered list
        for idx, layer in enumerate(filtered):
            current = scene.view_layers.find(layer.name)
            if current != -1 and current != idx:
                scene.view_layers.move(current, idx)

        for vl in list(scene.view_layers)[len(filtered):]:
            if vl.name not in names:
                try:
                    scene.view_layers.remove(vl)
                except RuntimeError as err:
                    _warn(str(err))

        return {"Scene": scene}


def register():
    bpy.utils.register_class(FNSetSceneViewlayers)


def unregister():
    bpy.utils.unregister_class(FNSetSceneViewlayers)