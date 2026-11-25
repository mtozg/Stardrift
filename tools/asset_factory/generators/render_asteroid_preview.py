import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="build/asteroid/asteroid_scene_r011.blend")
out="build/asteroid/asteroid_preview_r011.png"

# Dense sculpt meshes only; exported LOD meshes remain hidden in this preview.
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name.startswith("LOD"):
        ob.hide_render=True

def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()

target=Vector((0,0,0))
bpy.ops.object.camera_add(location=(0,-12.8,5.1))
cam=bpy.context.object
aim(cam,target)
cam.data.type="ORTHO"
cam.data.ortho_scale=11.8
bpy.context.scene.camera=cam

for loc,energy,size in [
    ((-4.5,-5.0,8.0),1850,5.0),
    ((5.0,-1.5,3.5),1250,4.0),
    ((0.0,5.0,6.5),1650,4.5)
]:
    bpy.ops.object.light_add(type="AREA",location=loc)
    light=bpy.context.object
    light.data.energy=energy
    light.data.shape="DISK"
    light.data.size=size
    aim(light,target)

scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.eevee.use_gtao=True
scene.eevee.gtao_distance=1.1
scene.eevee.gtao_factor=1.7
scene.render.resolution_x=1920
scene.render.resolution_y=1080
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.004,.005,.007,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.22
scene.view_settings.view_transform="Standard"
scene.view_settings.look="Medium High Contrast"
scene.render.filepath=out
bpy.ops.render.render(write_still=True)
print("PREVIEW_RENDERED",out)
