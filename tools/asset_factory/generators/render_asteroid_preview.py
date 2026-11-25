import bpy
from mathutils import Vector
out="build/asteroid/asteroid_preview_r007.png"
positions={"SCULPT_ASTEROID_FLAT":-3.15,"SCULPT_ASTEROID_ELONGATED":0,"SCULPT_ASTEROID_JAGGED":3.15}
for name,x in positions.items():bpy.data.objects[name].location.x=x
for o in bpy.context.scene.objects:
 if o.type=="MESH" and not o.name.startswith("SCULPT_"):o.hide_render=True
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
target=Vector((0,0,0));bpy.ops.object.camera_add(location=(0,-10.8,4.3));cam=bpy.context.object;aim(cam,target);cam.data.type="ORTHO";cam.data.ortho_scale=10.1;bpy.context.scene.camera=cam
for loc,e,s in [((-3,-5,7),1450,5.5),((4,-1,3),1050,4.5),((0,4,5),1250,5)]:
 bpy.ops.object.light_add(type="AREA",location=loc);a=bpy.context.object;a.data.energy=e;a.data.shape="DISK";a.data.size=s;aim(a,target)
sc=bpy.context.scene;sc.render.engine="BLENDER_EEVEE";sc.eevee.use_gtao=True;sc.eevee.gtao_distance=.85;sc.eevee.gtao_factor=1.65
sc.render.resolution_x=1600;sc.render.resolution_y=850;sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG";sc.world.color=(.008,.009,.012);sc.view_settings.view_transform="Standard";sc.view_settings.look="Medium High Contrast";sc.render.filepath=out;bpy.ops.render.render(write_still=True);print("PREVIEW_RENDERED",out)
