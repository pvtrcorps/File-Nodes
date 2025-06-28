"""Node to adjust collection visibility options per view layer."""

import bpy
from bpy.types import Node, PropertyGroup, UIList

from .base import FNBaseNode
from ..sockets import FNSocketViewLayer
from ..operators import auto_evaluate_if_enabled


class FNViewLayerCollectionState(PropertyGroup):
    """Stores visibility options for a collection in a view layer."""
    collection: bpy.props.PointerProperty(type=bpy.types.Collection)
    exclude: bpy.props.BoolProperty(name="Exclude", update=auto_evaluate_if_enabled)
    holdout: bpy.props.BoolProperty(name="Holdout", update=auto_evaluate_if_enabled)
    indirect_only: bpy.props.BoolProperty(name="Indirect Only", update=auto_evaluate_if_enabled)


class FN_UL_view_layer_collections(UIList):
    bl_idname = "FN_UL_view_layer_collections"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            name = item.collection.name if item.collection else "<None>"
            row.label(text=name)
            row.prop(item, "exclude", text="Excl")
            row.prop(item, "holdout", text="Hold")
            row.prop(item, "indirect_only", text="Indirect")


def _find_layer_collection(layer, collection):
    if layer.collection == collection:
        return layer
    for child in layer.children:
        found = _find_layer_collection(child, collection)
        if found:
            return found
    return None


class FNViewLayerVisibility(Node, FNBaseNode):
    """Adjust collection visibility for a view layer."""
    bl_idname = "FNViewLayerVisibility"
    bl_label = "ViewLayer Visibility"

    layer_states: bpy.props.CollectionProperty(type=FNViewLayerCollectionState)
    active_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "FileNodesTreeType"

    def init(self, context):
        self.inputs.new('FNSocketViewLayer', "View Layer")
        self.outputs.new('FNSocketViewLayer', "View Layer")

    def update(self):
        view_layer = self._get_view_layer_for_ui(bpy.context)
        try:
            self._sync_states(view_layer)
        except Exception:
            pass
        auto_evaluate_if_enabled(bpy.context)

    def _get_view_layer_for_ui(self, context):
        sock = self.inputs.get("View Layer")
        name = None
        if sock and not sock.is_linked:
            name = getattr(sock, "value", None)
        if name:
            return context.scene.view_layers.get(name)
        return context.view_layer if hasattr(context, "view_layer") else None

    def _sync_states(self, view_layer):
        if not view_layer:
            self.layer_states.clear()
            return
        valid = []

        def walk(layer):
            valid.append(layer.collection)
            for ch in layer.children:
                walk(ch)
        walk(view_layer.layer_collection)

        for i in reversed(range(len(self.layer_states))):
            if self.layer_states[i].collection not in valid:
                self.layer_states.remove(i)

        existing = {item.collection for item in self.layer_states}

        def add_items(layer):
            if layer.collection not in existing:
                item = self.layer_states.add()
                item.collection = layer.collection
                item.exclude = layer.exclude
                item.holdout = layer.holdout
                item.indirect_only = layer.indirect_only
                existing.add(layer.collection)
            for ch in layer.children:
                add_items(ch)
        add_items(view_layer.layer_collection)

    def draw_buttons(self, context, layout):
        view_layer = self._get_view_layer_for_ui(context)
        if not view_layer:
            layout.label(text="No View Layer")
            return
        layout.template_list(
            "FN_UL_view_layer_collections",
            "",
            self,
            "layer_states",
            self,
            "active_index",
            rows=3,
        )

    def process(self, context, inputs):
        view_layer = inputs.get("View Layer")
        if view_layer:
            self._sync_states(view_layer)
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            for item in self.layer_states:
                coll = item.collection
                if not coll:
                    continue
                layer = _find_layer_collection(view_layer.layer_collection, coll)
                if not layer:
                    continue
                if ctx:
                    ctx.store_original(layer, "exclude")
                    ctx.store_original(layer, "holdout")
                    ctx.store_original(layer, "indirect_only")
                try:
                    layer.exclude = item.exclude
                except Exception:
                    pass
                try:
                    layer.holdout = item.holdout
                except Exception:
                    pass
                try:
                    layer.indirect_only = item.indirect_only
                except Exception:
                    pass
        return {"View Layer": view_layer}


_classes = (
    FNViewLayerCollectionState,
    FN_UL_view_layer_collections,
    FNViewLayerVisibility,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

