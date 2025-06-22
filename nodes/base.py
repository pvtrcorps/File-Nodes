
import bpy

class FNBaseNode:
    '''Mixin to add a .process(context, inputs) stub'''
    bl_width_default = 160
    def process(self, context, inputs):
        return {}
