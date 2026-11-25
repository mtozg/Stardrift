import bpy, json, math, os, random, struct
from mathutils import Vector

# Stardrift env_rock_crystal PREVIEW r005
# Reference-led: weathered iron mass + one dense, embedded ruby cluster.
random.seed(251125)
OUT="build/asteroid"; os.makedirs(OUT,exist_ok=True)
GLB=os.path.join(OUT,"sd_env_rock_crystal_r005.glb")
QC=os.path.join(OUT,"qc_report.json")
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)

def mat(name,color,metal,rough):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    return m

rock=mat("MAT_body",(0.105,0.092,0.083),0.28,0.84)
p=rock.node_tree.nodes.get("Principled BSDF")
# Baked-looking relief is modeled into the silhouette; procedural nodes are preview-only.
crystal=mat("MAT_crystal",(0.42,0.012,0.035),0.08,0.19)
dark=mat("MAT_crystal_shadow",(0.105,0.004,0.012),0.06,0.28)
parts=[]

# Compact but irregular iron body. Displacement creates impact cavities and broken edges.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1)
body=bpy.context.object; body.name="LOD0_body"
body.scale=(1.38,1.18,1.12)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for name,scale,strength in [("TX_large_fractures",0.23,0.30),("TX_small_pits",0.085,0.075)]:
    tx=bpy.data.textures.new(name,type="CLOUDS"); tx.noise_scale=scale; tx.noise_depth=2
    mod=body.modifiers.new(name,"DISPLACE"); mod.texture=tx; mod.strength=strength
    bpy.context.view_layer.objects.active=body; bpy.ops.object.modifier_apply(modifier=mod.name)
body.data.materials.append(rock); parts.append(body)

normal=Vector((0.12,-0.97,0.20)).normalized()
tangent=normal.cross(Vector((0,0,1))).normalized()
bitangent=normal.cross(tangent).normalized()
def surface(v):
    x,y,z=v
    k=1/math.sqrt((x/1.38)**2+(y/1.18)**2+(z/1.12)**2)
    return Vector((x*k,y*k,z*k))
cluster=surface(normal)*0.99

def shard(root,direction,length,radius,idx):
    direction=direction.normalized()
    u=direction.cross(Vector((0,0,1)))
    if u.length<0.05: u=direction.cross(Vector((0,1,0)))
    u.normalize(); v=direction.cross(u).normalized()
    sides=5; verts=[]; faces=[]
    phase=random.uniform(0,math.tau)
    # Broad root is buried into the ore; shoulder and pointed tip catch ruby highlights.
    for z,fac in [(0.0,0.88),(length*0.72,0.62),(length,0.012)]:
        for j in range(sides):
            a=phase+math.tau*j/sides
            rr=radius*fac*random.uniform(0.88,1.12)
            q=root+direction*z+u*math.cos(a)*rr+v*math.sin(a)*rr
            verts.append(tuple(q))
    faces.append(tuple(reversed(range(sides))))
    for ring in range(2):
        for j in range(sides):
            a=ring*sides+j; b=ring*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(range(2*sides,3*sides)))
    mesh=bpy.data.meshes.new("ruby_facet_mesh"); mesh.from_pydata(verts,[],faces)
    mesh.materials.append(crystal); mesh.materials.append(dark)
    ob=bpy.data.objects.new("ruby_shard_%02d"%idx,mesh); bpy.context.collection.objects.link(ob)
    for poly in mesh.polygons:
        if random.random()<0.22: poly.material_index=1
    parts.append(ob)

# 12 large interlocking points: one asymmetric fan, not scattered spikes.
specs=[
 (-.30,-.12,.76,.115),(-.21,.02,.92,.13),(-.11,-.08,1.12,.145),
 (0.02,.02,1.20,.15),(.16,-.06,1.03,.14),(.28,.02,.87,.125),
 (-.23,.17,.70,.105),(-.08,.19,.82,.11),(.10,.18,.88,.12),(.25,.17,.68,.10),
 (-.02,-.23,.72,.10),(.15,-.21,.66,.095)
]
for i,(x,y,L,R) in enumerate(specs):
    off=tangent*x+bitangent*y
    root=cluster+off-normal*0.20
    direction=(normal+tangent*x*0.65+bitangent*y*0.55).normalized()
    shard(root,direction,L,R,i)

# Four small fractured facets fill the seam at its base.
for i in range(4):
    x=random.uniform(-.19,.19); y=random.uniform(-.12,.12)
    root=cluster+tangent*x+bitangent*y-normal*0.12
    shard(root,(normal+tangent*x+bitangent*y).normalized(),random.uniform(.20,.29),random.uniform(.045,.06),i+12)

# One draw call: join all geometry while preserving the three material slots.
bpy.ops.object.select_all(action="DESELECT")
for ob in parts: ob.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.object.join(); lod0=bpy.context.object; lod0.name="LOD0_body"
lods=[lod0]
for name,ratio in [("LOD1_body",.375),("LOD2_body",.125)]:
    dup=lod0.copy(); dup.data=lod0.data.copy(); bpy.context.collection.objects.link(dup); dup.name=name
    dec=dup.modifiers.new("LOD reduction","DECIMATE"); dec.ratio=ratio
    bpy.context.view_layer.objects.active=dup; bpy.ops.object.modifier_apply(modifier=dec.name); lods.append(dup)

bpy.ops.object.select_all(action="DESELECT")
for ob in lods: ob.select_set(True)
bpy.context.view_layer.objects.active=lod0
bpy.ops.export_scene.gltf(filepath=GLB,export_format="GLB",use_selection=True,export_apply=True)
def tris(ob): return sum(max(0,len(poly.vertices)-2) for poly in ob.data.polygons)
with open(GLB,"rb") as f: magic,version,size=struct.unpack("<4sII",f.read(12))
report={"asset_id":"env_rock_crystal","revision":"r005","generator":"Blender Python","blender_version":bpy.app.version_string,
"file":os.path.basename(GLB),"glb_bytes":os.path.getsize(GLB),"glb_header_valid":magic==b"glTF" and version==2 and size==os.path.getsize(GLB),
"lod_triangles":{o.name:tris(o) for o in lods},"material_slots":len(lod0.data.materials),"crystal_shards":len(specs)+4,
"target_env_rock_lod0_triangles":400,"target_env_rock_glb_bytes":40960,"status":"prototype_r005_pending_visual_approval"}
with open(QC,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
