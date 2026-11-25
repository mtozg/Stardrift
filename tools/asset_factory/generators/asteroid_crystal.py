import bpy, json, math, os, random, struct
from mathutils import Vector

# Stardrift env_rock PREVIEW r006 — crystal-free asteroid silhouette study.
# Three distinct irregular bodies; impact basins are sculpted into the mesh.
random.seed(260125)
OUT="build/asteroid"; os.makedirs(OUT,exist_ok=True)
GLB=os.path.join(OUT,"sd_env_rock_variants_r006.glb")
QC=os.path.join(OUT,"qc_report_r006.json")
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)

def make_material():
    m=bpy.data.materials.new("MAT_body"); m.diffuse_color=(0.105,0.098,0.087,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(0.105,0.098,0.087,1)
    p.inputs["Metallic"].default_value=0.12
    p.inputs["Roughness"].default_value=0.91
    return m
rock=make_material()

# (name, scale, crater count, seed, base irregularity)
variants=[
 ("ASTEROID_FLAT", (1.42,1.08,0.78), 18, 601, 0.13),
 ("ASTEROID_ELONGATED", (1.58,0.88,0.98), 15, 602, 0.15),
 ("ASTEROID_JAGGED", (1.22,1.08,1.12), 21, 603, 0.22),
]
all_lods=[]; qc={}
for name,scale,crater_count,seed,roughness in variants:
    rng=random.Random(seed)
    # Deterministic crater centers distributed over the sphere.
    craters=[]
    for i in range(crater_count):
        z=rng.uniform(-0.88,0.88); a=rng.uniform(0,math.tau)
        d=Vector((math.sqrt(1-z*z)*math.cos(a), math.sqrt(1-z*z)*math.sin(a), z))
        craters.append((d,rng.uniform(0.10,0.24),rng.uniform(0.035,0.085)))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1)
    body=bpy.context.object; body.name="LOD0_"+name
    verts=[]
    for vert in body.data.vertices:
        d=vert.co.normalized()
        # Broad lumpy mass plus smaller unevenness; no perfect spherical outline.
        n=math.sin(d.x*8.1+seed)*math.sin(d.y*6.7-seed*.01)*math.cos(d.z*7.3)
        n2=math.sin(d.x*17.0+d.z*11.0)*math.cos(d.y*14.0)
        radial=1.0+roughness*(0.55*n+0.22*n2)
        # Each impact has a depressed bowl and a slightly raised broken rim.
        for center,rad,depth in craters:
            dot=max(-1.0,min(1.0,d.dot(center)))
            ang=math.acos(dot)
            if ang < rad*1.65:
                x=ang/rad
                bowl=-depth*math.exp(-((x/0.72)**2)*1.8)
                rim=depth*0.22*math.exp(-(((x-1.03)/0.19)**2))
                radial += bowl+rim
        # Small fractured edge variation.
        radial += roughness*0.10*math.sin(d.x*31+d.y*19+d.z*23)
        q=Vector((d.x*scale[0]*radial,d.y*scale[1]*radial,d.z*scale[2]*radial))
        verts.append(q)
    for v,q in zip(body.data.vertices,verts): v.co=q
    body.data.update()
    body.data.materials.append(rock)
    # Flat facets catch the light like broken mineral rock.
    for poly in body.data.polygons: poly.use_smooth=False
    base_tri=sum(max(0,len(p.vertices)-2) for p in body.data.polygons)
    lods=[body]
    for lod_name,ratio in [("LOD1_"+name,.46),("LOD2_"+name,.155)]:
        dup=body.copy(); dup.data=body.data.copy(); bpy.context.collection.objects.link(dup); dup.name=lod_name
        dec=dup.modifiers.new("LOD reduction","DECIMATE"); dec.ratio=ratio
        bpy.context.view_layer.objects.active=dup; bpy.ops.object.modifier_apply(modifier=dec.name)
        lods.append(dup)
    all_lods.extend(lods)
    qc[name]={"lod_triangles":{o.name:sum(max(0,len(p.vertices)-2) for p in o.data.polygons) for o in lods},
              "crater_count":crater_count,"material_slots":1}
# Keep all 3 variations and their LODs as separately named meshes in one review GLB.
bpy.ops.object.select_all(action="DESELECT")
for ob in all_lods: ob.select_set(True)
bpy.context.view_layer.objects.active=all_lods[0]
bpy.ops.export_scene.gltf(filepath=GLB,export_format="GLB",use_selection=True,export_apply=True)
with open(GLB,"rb") as f: magic,version,size=struct.unpack("<4sII",f.read(12))
report={"asset_id":"env_rock","revision":"r006","status":"crystal_free_silhouette_study_pending_visual_approval",
        "file":os.path.basename(GLB),"glb_bytes":os.path.getsize(GLB),
        "glb_header_valid":magic==b"glTF" and version==2 and size==os.path.getsize(GLB),
        "target_env_rock_lod0_triangles":400,"target_env_rock_lod1_triangles":150,
        "target_env_rock_lod2_triangles":50,"target_glb_bytes":40960,"variants":qc}
with open(QC,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
