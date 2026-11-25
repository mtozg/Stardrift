import bpy, math
from mathutils import Vector

src="build/asteroid/sd_env_rock_crystal_r005.glb"
out="build/asteroid/asteroid_preview_r005.png"
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=src)
objects=[o for o in bpy.context.scene.objects if o.type=="MESH"]
corners=[o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
mins=Vector((min(v[i] for v in corners) for i in range(3)))
maxs=Vector((max(v[i] for v in corners) for i in range(3)))
center=(mins+maxs)/2; radius=max((maxs-mins).length/2,1.0)
def aim(obj,point): obj.rotation_euler=(Vector(point)-obj.location).to_track_quat("-Z","Y").to_euler()
# Three-quarter hero angle: expose the crystal fan and the deeply fractured iron shell.
bpy.ops.object.camera_add(location=center+Vector((radius*1.45,-radius*2.65,radius*0.92)))
cam=bpy.context.object; aim(cam,center); cam.data.lens=62; bpy.context.scene.camera=cam
for loc,energy,size in [
 (center+Vector((radius*1.2,-radius*2.0,radius*2.0)),650,radius*1.35),
 (center+Vector((-radius*2.0,-radius*0.2,radius*0.45)),390,radius*1.8),
 (center+Vector((radius*0.4,radius*1.8,radius*0.9)),500,radius*1.35),
]:
 bpy.ops.object.light_add(type="AREA",location=loc); light=bpy.context.object
 light.data.energy=energy; light.data.shape="DISK"; light.data.size=size; aim(light,center)
scene=bpy.context.scene; scene.render.engine="BLENDER_EEVEE"; scene.eevee.use_gtao=True
scene.eevee.gtao_distance=2.2; scene.eevee.gtao_factor=1.45
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
scene.world.color=(0.009,0.011,0.016)
scene.view_settings.view_transform="Standard"; scene.view_settings.look="Medium High Contrast"
scene.render.filepath=out; bpy.ops.render.render(write_still=True)
print("PREVIEW_RENDERED",out)
