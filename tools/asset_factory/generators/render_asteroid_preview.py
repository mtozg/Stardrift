import bpy, math
from mathutils import Vector

src="build/asteroid/sd_env_rock_variants_r006.glb"
out="build/asteroid/asteroid_preview_r006.png"
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=src)
# Show only LOD0 meshes, arranged as a three-way comparison.
names=["ASTEROID_FLAT","ASTEROID_ELONGATED","ASTEROID_JAGGED"]
objs=[]
for name in names:
    ob=bpy.data.objects.get("LOD0_"+name)
    if ob:
        ob.location.x={"ASTEROID_FLAT":-3.15,"ASTEROID_ELONGATED":0.0,"ASTEROID_JAGGED":3.15}[name]
        objs.append(ob)
for ob in list(bpy.context.scene.objects):
    if ob.type=="MESH" and not ob.name.startswith("LOD0_"): ob.hide_render=True
# A single studio camera and broad lights reveal the crater bowls and irregular silhouettes.
target=Vector((0,0,0))
def aim(obj,point): obj.rotation_euler=(Vector(point)-obj.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(0,-10.8,5.0))
cam=bpy.context.object; aim(cam,target); cam.data.type="ORTHO"; cam.data.ortho_scale=10.2
bpy.context.scene.camera=cam
for loc,energy,size in [((-3,-5,7),1250,6),( (4,-1,3),850,5),((0,4,5),1000,5)]:
    bpy.ops.object.light_add(type="AREA",location=loc); l=bpy.context.object
    l.data.energy=energy; l.data.shape="DISK"; l.data.size=size; aim(l,target)
scene=bpy.context.scene; scene.render.engine="BLENDER_EEVEE"; scene.eevee.use_gtao=True
scene.eevee.gtao_distance=1.6; scene.eevee.gtao_factor=1.55
scene.render.resolution_x=1600; scene.render.resolution_y=850; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"; scene.render.film_transparent=False
scene.world.color=(0.012,0.013,0.016)
scene.view_settings.view_transform="Standard"; scene.view_settings.look="Medium High Contrast"
scene.render.filepath=out; bpy.ops.render.render(write_still=True)
print("PREVIEW_RENDERED",out)
