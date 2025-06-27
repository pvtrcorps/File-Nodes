
bl_info = {
    "name": "File Nodes MVP",
    "author": "ChatGPT (MVP generator)",
    "version": (0, 1, 0),
    "blender": (4, 4, 0),
    "location": "Node Editor > File Nodes",
    "description": "Prototype node-based file/scene management",
    "category": "Object",
}

# Keep a reference to the addon name so other modules can access
# preferences without guessing the package string.
ADDON_NAME = __name__

try:
    import bpy
except Exception:  # pragma: no cover - allow running tests without bpy
    bpy = None

if bpy and __package__:
    import importlib
    from . import tree, sockets, nodes, operators, ui, menu
    modules = [tree, sockets, nodes, operators, ui, menu]
    addon_keymaps = []
else:  # Running outside Blender or without a package context
    modules = []


if bpy and getattr(getattr(bpy, 'types', None), 'AddonPreferences', None):
    class FileNodesPreferences(bpy.types.AddonPreferences):
        bl_idname = ADDON_NAME

        auto_evaluate: bpy.props.BoolProperty(
            name="Auto Evaluate",
            description="Automatically evaluate node trees when properties change",
            default=False,
        )

        def draw(self, context):
            layout = self.layout
            layout.prop(self, "auto_evaluate")

    def register():
        bpy.utils.register_class(FileNodesPreferences)
        for m in modules:
            importlib.reload(m)
            if hasattr(m, "register"):
                m.register()
        wm = getattr(getattr(bpy, "context", None), "window_manager", None)
        kc = getattr(getattr(wm, "keyconfigs", None), "addon", None)
        if kc:
            km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")
            kmi = km.keymap_items.new("file_nodes.group_nodes", "G", "PRESS", ctrl=True)
            addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new(
                "file_nodes.ungroup_nodes", "G", "PRESS", ctrl=True, alt=True
            )
            addon_keymaps.append((km, kmi))

    def unregister():
        for km, kmi in addon_keymaps:
            try:
                km.keymap_items.remove(kmi)
            except Exception:
                pass
        addon_keymaps.clear()
        for m in reversed(modules):
            if hasattr(m, "unregister"):
                m.unregister()
        bpy.utils.unregister_class(FileNodesPreferences)
else:  # pragma: no cover - noop if bpy is unavailable
    def register():
        pass

    def unregister():
        pass
