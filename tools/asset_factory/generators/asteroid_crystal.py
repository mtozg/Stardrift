import bpy, json, math, os, random, struct
from mathutils import Vector

random.seed(241126)
OUT = "build/asteroid"
os.makedirs(OUT, exist_ok=True)
GLB = os.path.join(OUT, "sd_env_rock_crystal_r003.glb")
QC = os.path.join(OUT, "qc_report.json")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def make_mat(name, color, metallic, roughness):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=roughness
    return m

# Iron-rich, weathered rock: dark gunmetal, oxidized red-brown patches, chipped relief.
rock=make_mat("MAT_body",(0.075,0.055,0.045),0.18,0.88)
nt=rock.node_tree; n=nt.nodes; l=nt.links; bs=n.get("Principled BSDF")
bs.inputs["Base Color"].default_value=(0.075,0.055,0.045,1)
coord=n.new("ShaderNodeTexCoord")
large=n.new("ShaderNodeTexNoise"); large.inputs["Scale"].default_value=3.8; large.inputs["Detail"].default_value=5.0; large.inputs["Roughness"].default_value=0.78
fine=n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value=28.0; fine.inputs["Detail"].default_value=4.0; fine.inputs["Roughness"].default_value=0.82
l.new(coord.outputs["Generated"],large.inputs["Vector"]); l.new(coord.outputs["Generated"],fine.inputs["Vector"])
r=n.new("ShaderNodeValToRGB")
cr=r.color_ramp
cr.elements[0].position=0.18; cr.elements[0].color=(0.018,0.019,0.021,1)
cr.elements[1].position=0.83; cr.elements[1].color=(0.34,0.29,0.23,1)
e=cr.elements.new(0.43); e.color=(0.075,0.065,0.058,1)
e=cr.elements.new(0.64); e.color=(0.22,0.075,0.045,1)
l.new(large.outputs["Fac"],r.inputs["Fac"])
b=n.new("ShaderNodeBump"); b.inputs["Strength"].default_value=0.48; b.inputs["Distance"].default_value=0.11
l.new(fine.outputs["Fac"],b.inputs["Height"]); l.new(b.outputs["Normal"],bs.inputs["Normal"])
# Fine grain also roughens the surface; avoid a plastic highlight.
rough=n.new("ShaderNodeMapRange"); rough.inputs["From Min"].default_value=0; rough.inputs["From Max"].default_value=1
rough.inputs["To Min"].default_value=0.68; rough.inputs["To Max"].default_value=0.98
l.new(fine.outputs["Fac"],rough.inputs["Value"]); l.new(rough.outputs["Result"],bs.inputs["Roughness"])

crystal=make_mat("MAT_crystal",(0.34,0.012,0.028),0.12,0.24)
p=crystal.node_tree.nodes.get("Principled BSDF")
# Slight internal red depth, no self-illumination.
crystal_dark=make_mat("MAT_crystal_shadow",(0.12,0.006,0.014),0.08,0.31)
parts=[]
def add(obj,mat,name):
    obj.name=name; obj.data.materials.append(mat); parts.append(obj); return obj

# Rugged, asymmetrical iron core. Dense enough to carry a broken silhouette within the mobile budget.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1)
core=bpy.context.object
core.scale=(1.42,1.20,1.08)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
tex=bpy.data.textures.new("TX_multiscale_iron_fracture",type="CLOUDS")
tex.noise_scale=0.19; tex.noise_depth=2
d=core.modifiers.new("Large fractured silhouette","DISPLACE"); d.texture=tex; d.strength=0.34
bpy.context.view_layer.objects.active=core; bpy.ops.object.modifier_apply(modifier=d.name)
# Add a second, finer displacement pass for chipped edges and impact scars.
tex2=bpy.data.textures.new("TX_chipped_edges",type="CLOUDS"); tex2.noise_scale=0.075; tex2.noise_depth=1
d=core.modifiers.new("Small chipped relief","DISPLACE"); d.texture=tex2; d.strength=0.075
bpy.ops.object.modifier_apply(modifier=d.name)
d=core.modifiers.new("Mobile triangle budget","DECIMATE"); d.ratio=0.68
bpy.ops.object.modifier_apply(modifier=d.name)
add(core,rock,"iron_rock_body")

# Build a single prominent crystal seam on one face, matching the existing red ore artwork.
patch_normal=Vector((0.16,-0.96,0.22)).normalized()
tangent=patch_normal.cross(Vector((0,0,1))).normalized()
bitangent=patch_normal.cross(tangent).normalized()
def surface_point(v):
    # Approximate ellipsoid intersection along direction.
    x,y,z=v
    k=1.0/math.sqrt((x/1.42)**2+(y/1.20)**2+(z/1.08)**2)
    return Vector((x*k,y*k,z*k))
base=surface_point(patch_normal)*0.99
# Embedded dark crystal roots, clustered tightly at the seam.
shards=0
specs=[
 (-0.23,-0.06,0.46,0.105),(-0.13,0.04,0.63,0.12),(-0.02,-0.03,0.78,0.13),
 (0.12,0.04,0.58,0.115),(0.23,-0.02,0.69,0.12),(0.02,0.17,0.48,0.09),
 (-0.19,0.16,0.39,0.085),(0.20,0.17,0.43,0.09),(0.00,-0.18,0.52,0.10),
]
def make_shard(pos, direction, length, radius, idx):
    # Irregular hexagonal prism tapering to a sharp point; crystal roots sit below the rock surface.
    direction=direction.normalized()
    u=direction.cross(Vector((0,0,1)))
    if u.length<0.05: u=direction.cross(Vector((0,1,0)))
    u.normalize(); v=direction.cross(u).normalized()
    verts=[]; faces=[]; sides=6
    rings=[(0.0,0.78),(length*0.78,0.54),(length,0.015)]
    phase=random.uniform(0,math.tau)
    for z,scale in rings:
        for j in range(sides):
            a=phase+math.tau*j/sides
            rr=radius*scale*random.uniform(0.92,1.08)
            q=pos+direction*z+u*(math.cos(a)*rr)+v*(math.sin(a)*rr)
            verts.append(tuple(q))
    faces.append(tuple(reversed(range(sides))))
    for ring in range(2):
        for j in range(sides):
            a=ring*sides+j; b=ring*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(range(2*sides,3*sides)))
    mesh=bpy.data.meshes.new("crystal_facets"); mesh.from_pydata(verts,[],faces); mesh.materials.append(crystal); mesh.materials.append(crystal_dark)
    ob=bpy.data.objects.new("crystal_shard",mesh); bpy.context.collection.objects.link(ob)
    for poly in mesh.polygons:
        if random.random()<0.28: poly.material_index=1
    parts.append(ob)
for i,(ox,oy,length,radius) in enumerate(specs):
    offset=tangent*ox+bitangent*oy
    root=base+offset-patch_normal*0.16
    direction=(patch_normal+tangent*(ox*0.75)+bitangent*(oy*0.6)).normalized()
    make_shard(root,direction,length,radius,i); shards+=1

# A few tiny fractured crystal splinters at the seam edge, not scattered turquoise spikes.
for i in range(4):
    ox=random.choice([-1,1])*random.uniform(0.22,0.34)
    oy=random.uniform(-0.12,0.18)
    root=base+tangent*ox+bitangent*oy-patch_normal*0.08
    direction=(patch_normal+tangent*ox*0.45+bitangent*oy*0.4).normalized()
    make_shard(root,direction,random.uniform(0.18,0.28),random.uniform(0.035,0.05),i+20)
    shards+=1

# Join to one draw-call mesh while retaining separate material slots.
bpy.ops.object.select_all(action="DESELECT")
for obj in parts: obj.select_set(True)
bpy.context.view_layer.objects.active=core
bpy.ops.object.join()
lod0=bpy.context.object; lod0.name="LOD0_body"
lods=[lod0]
for name,ratio in (("LOD1_body",0.45),("LOD2_body",0.15)):
    dup=lod0.copy(); dup.data=lod0.data.copy(); bpy.context.collection.objects.link(dup); dup.name=name
    dec=dup.modifiers.new("LOD reduction","DECIMATE"); dec.ratio=ratio
    bpy.context.view_layer.objects.active=dup; bpy.ops.object.modifier_apply(modifier=dec.name); lods.append(dup)

bpy.ops.object.select_all(action="DESELECT")
for obj in lods: obj.select_set(True)
bpy.context.view_layer.objects.active=lod0
bpy.ops.export_scene.gltf(filepath=GLB,export_format="GLB",use_selection=True,export_apply=True)
def tris(obj): return sum(max(0,len(poly.vertices)-2) for poly in obj.data.polygons)
with open(GLB,"rb") as f: magic,version,declared=struct.unpack("<4sII",f.read(12))
report={"asset_id":"env_rock_crystal","revision":"r003","generator":"Blender Python","blender_version":bpy.app.version_string,"file":os.path.basename(GLB),"glb_bytes":os.path.getsize(GLB),"glb_header_valid":magic==b"glTF" and version==2 and declared==os.path.getsize(GLB),"lod_triangles":{o.name:tris(o) for o in lods},"material_slots":len(lod0.data.materials),"crystal_shards":shards,"mineral_veins":0,"target_env_rock_lod0_triangles":400,"target_env_rock_glb_bytes":40960,"status":"prototype_r003_pending_visual_approval"}
with open(QC,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
