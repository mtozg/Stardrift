import bpy, math, os
from mathutils import Vector

src = "build/asteroid/sd_env_rock_crystal_r003.glb"
out = "build/asteroid/asteroid_preview_r003.png"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=src)

objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
corners = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
mins = Vector((min(v[i] for v in corners) for i in range(3)))
maxs = Vector((max(v[i] for v in corners) for i in range(3)))
center = (mins + maxs) / 2
radius = max((maxs - mins).length / 2, 1.0)

def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()

bpy.ops.object.camera_add(location=center + Vector((radius*0.42, -radius*2.75, radius*0.63)))
cam = bpy.context.object
aim(cam, center)
cam.data.lens = 72
bpy.context.scene.camera = cam

for loc, energy, size in [
    (center + Vector((radius*1.0, -radius*2.0, radius*2.2)), 1500, radius*1.6),
    (center + Vector((-radius*2.0, -radius*0.4, radius*0.8)), 700, radius*2.0),
    (center + Vector((radius*0.3, radius*2.0, radius*1.0)), 900, radius*1.8),
]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    aim(light, center)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.eevee.use_gtao = True
scene.eevee.gtao_distance = 3
scene.eevee.gtao_factor = 1.35
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.world.color = (0.012, 0.018, 0.03)
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("PREVIEW_RENDERED", out)
