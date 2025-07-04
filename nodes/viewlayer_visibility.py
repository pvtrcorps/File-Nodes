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
    depth: bpy.props.IntProperty()
    expanded: bpy.props.BoolProperty(name="Expanded", default=True)
    parent_index: bpy.props.IntProperty(default=-1)
    has_children: bpy.props.BoolProperty(default=False)


class FN_UL_view_layer_collections(UIList):
    bl_idname = "FN_UL_view_layer_collections"

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = []
        for idx, item in enumerate(items):
            visible = True
            parent_idx = getattr(item, "parent_index", -1)
            while parent_idx != -1:
                parent = items[parent_idx]
                if not parent.expanded:
                    visible = False
                    break
                parent_idx = parent.parent_index
            flt_flags.append(self.bitflag_filter_item if visible else 0)
        return flt_flags, []

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7, align=True)
            name_row = split.row(align=True)
            for _ in range(getattr(item, "depth", 0)):
                name_row.label(icon='BLANK1', text="")
            if item.has_children:
                name_row.prop(
                    item,
                    "expanded",
                    text="",
                    icon='TRIA_DOWN' if item.expanded else 'TRIA_RIGHT',
                    emboss=False,
                )
            else:
                name_row.label(icon='BLANK1', text="")
            name = item.collection.name if item.collection else "<None>"
            icon_name = 'OUTLINER_COLLECTION' if item.collection else 'DOT'
            name_row.label(text=name, icon=icon_name)

            icon_row = split.row(align=True)
            icon_row.alignment = 'RIGHT'
            icon_row.prop(
                item,
                "exclude",
                text="",
                icon='CHECKBOX_DEHLT' if item.exclude else 'CHECKBOX_HLT',
                emboss=False,
            )
            icon_row.prop(
                item,
                "holdout",
                text="",
                icon='HOLDOUT_ON' if item.holdout else 'HOLDOUT_OFF',
                emboss=False,
            )
            icon_row.prop(
                item,
                "indirect_only",
                text="",
                icon='INDIRECT_ONLY_ON' if item.indirect_only else 'INDIRECT_ONLY_OFF',
                emboss=False,
            )


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
        sock = self.inputs.new('FNSocketViewLayer', "View Layer")
        sock.is_mutable = False
        self.outputs.new('FNSocketViewLayer', "View Layer")

    def update(self):
        # Only trigger evaluation when properties change. The collection
        # states are synchronized during node execution to avoid overwriting
        # user settings with the current scene state.
        auto_evaluate_if_enabled(bpy.context)

    def _get_view_layer_for_ui(self, context):
        stored = getattr(self, "_input_view_layer", None)
        if stored:
            return stored
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
        active_coll = None
        if 0 <= self.active_index < len(self.layer_states):
            active_coll = self.layer_states[self.active_index].collection

        def collect(layer, depth=0, parent=-1, items=None):
            if items is None:
                items = []
            coll = layer.collection
            if getattr(coll, "is_embedded_data", False):
                for ch in layer.children:
                    collect(ch, depth + 1, parent, items)
                return items
            idx = len(items)
            items.append((coll, depth, parent, bool(layer.children)))
            for ch in layer.children:
                collect(ch, depth + 1, idx, items)
            return items

        states = collect(view_layer.layer_collection)
        if getattr(view_layer.layer_collection.collection, "is_embedded_data", False):
            states = [
                (c, d - 1, p, has)
                for c, d, p, has in states
            ]

        old = {}
        for item in self.layer_states:
            old[item.collection.as_pointer()] = (
                item.exclude,
                item.holdout,
                item.indirect_only,
                item.expanded,
            )
        self.layer_states.clear()
        for coll, depth, parent, has_children in states:
            item = self.layer_states.add()
            item.collection = coll
            ex, ho, ind, exp = old.get(coll.as_pointer(), (False, False, False, True))
            item.exclude = ex
            item.holdout = ho
            item.indirect_only = ind
            item.expanded = exp
            item.depth = depth
            item.parent_index = parent
            item.has_children = has_children

        if active_coll:
            for idx, item in enumerate(self.layer_states):
                if item.collection == active_coll:
                    self.active_index = idx
                    break

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

    def process(self, context, inputs, manager):
        view_layer = inputs.get("View Layer")
        if view_layer:
            self._input_view_layer = view_layer
            self._sync_states(view_layer)
            ctx = getattr(getattr(self, "id_data", None), "fn_inputs", None)
            for item in self.layer_states:
                coll = item.collection
                if not coll:
                    continue
                layer = _find_layer_collection(view_layer.layer_collection, coll)
                if not layer:
                    continue
                
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