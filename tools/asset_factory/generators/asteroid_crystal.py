import bpy, json, math, os, random, struct
from mathutils import Vector
OUT="build/asteroid"
os.makedirs(OUT,exist_ok=True)
GLB=OUT+"/sd_env_rock_variants_r008.glb"
QC=OUT+"/qc_report_r008.json"

# Clean scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Weathered iron material: procedural detail is baked into the render only;
# exported GLB keeps a simple metallic-roughness material.
mat=bpy.data.materials.new("MAT_asteroid_weathered_iron")
mat.diffuse_color=(.105,.095,.083,1)
mat.use_nodes=True
nodes=mat.node_tree.nodes
links=mat.node_tree.links
bs=nodes.get("Principled BSDF")
bs.inputs["Base Color"].default_value=(.105,.095,.083,1)
bs.inputs["Metallic"].default_value=.12
bs.inputs["Roughness"].default_value=.92
noise=nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=7.5
noise.inputs["Detail"].default_value=9
noise.inputs["Roughness"].default_value=.78
ramp=nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color=(.018,.019,.020,1)
ramp.color_ramp.elements[1].color=(.25,.23,.20,1)
bump=nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.62
bump.inputs["Distance"].default_value=.12
links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
links.new(noise.outputs["Fac"],bump.inputs["Height"])
links.new(bump.outputs["Normal"],bs.inputs["Normal"])

# Irregular, fused rock masses. Metaballs create a genuinely lumpy 3D body,
# rather than a deformed sphere. Crater bowls are sculpted into the fused shell.
variants=[
 ("ASTEROID_MASSIVE", 811, (-1.45,1.22,1.12), 9),
 ("ASTEROID_SPLIT",   812, (-1.28,1.48,.98), 10),
 ("ASTEROID_RUGGED",  813, (-1.38,1.26,1.34), 11),
]
export_objects=[]
variant_info={}
for name,seed,scale,chunks in variants:
    rng=random.Random(seed)
    mb=bpy.data.metaballs.new("META_"+name)
    mb.resolution=.055
    mb.render_resolution=.045
    mb.threshold=.62
    obj=bpy.data.objects.new("META_"+name,mb)
    bpy.context.collection.objects.link(obj)
    # A dominant irregular core plus overlapping lobes of different sizes.
    mb.elements.new().co=(0,0,0)
    mb.elements[0].radius=1.18
    for i in range(chunks):
        az=rng.uniform(0,math.tau)
        z=rng.uniform(-.82,.82)
        rr=math.sqrt(max(.02,1-z*z))*rng.uniform(.48,.98)
        pos=Vector((rr*math.cos(az),rr*math.sin(az),z))*rng.uniform(.55,1.05)
        el=mb.elements.new()
        el.co=pos
        el.radius=rng.uniform(.48,.92)
        el.stiffness=rng.uniform(1.7,2.4)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target="MESH")
    rock=bpy.context.object
    rock.name="SCULPT_"+name
    rock.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

    # Voxel remesh fuses the lobes into one continuous, rough mass.
    rem=rock.modifiers.new("Fused rock surface","REMESH")
    rem.mode="VOXEL"
    rem.voxel_size=.052
    bpy.context.view_layer.objects.active=rock
    bpy.ops.object.modifier_apply(modifier=rem.name)
    smooth=rock.modifiers.new("Very light rock relaxation","SMOOTH")
    smooth.factor=.42
    smooth.iterations=2
    bpy.ops.object.modifier_apply(modifier=smooth.name)

    # Multi-scale displacement: broad fracture planes + small-scale erosion.
    tex=bpy.data.textures.new("erosion_"+name,type="CLOUDS")
    tex.noise_scale=.19
    tex.noise_depth=2
    disp=rock.modifiers.new("Eroded surface","DISPLACE")
    disp.texture=tex
    disp.strength=.19
    disp.mid_level=.52
    bpy.ops.object.modifier_apply(modifier=disp.name)
    tex2=bpy.data.textures.new("pitting_"+name,type="CLOUDS")
    tex2.noise_scale=.065
    tex2.noise_depth=2
    disp2=rock.modifiers.new("Fine pitting","DISPLACE")
    disp2.texture=tex2
    disp2.strength=.055
    disp2.mid_level=.52
    bpy.ops.object.modifier_apply(modifier=disp2.name)

    # Actual crater bowls with raised broken rims, distributed over the body.
    center=rock.location.copy()
    crater_count=14+rng.randrange(7)
    directions=[]
    for j in range(crater_count):
        z=rng.uniform(-.92,.92)
        a=rng.random()*math.tau
        d=Vector((math.sqrt(1-z*z)*math.cos(a),math.sqrt(1-z*z)*math.sin(a),z))
        directions.append((d,rng.uniform(.12,.28),rng.uniform(.075,.17)))
    for v in rock.data.vertices:
        p=v.co
        radial=Vector((p.x/scale[0],p.y/scale[1],p.z/scale[2]))
        if radial.length==0: continue
        d0=radial.normalized()
        offset=0.0
        for direction,radius,depth in directions:
            angle=math.acos(max(-1.0,min(1.0,d0.dot(direction))))
            x=angle/radius
            if x<1.65:
                bowl=-depth*math.exp(-((x/.63)**2)*1.8)
                rim=depth*.32*math.exp(-(((x-1.0)/.19)**2))
                broken=depth*.055*math.sin(x*29+seed)*math.exp(-((x-1.0)/.32)**2)
                offset+=bowl+rim+broken
        offset+=.018*math.sin(p.x*31+p.y*17)*math.cos(p.z*27)
        v.co += v.normal*offset
    rock.data.update()
    rock.data.materials.append(mat)
    for poly in rock.data.polygons:
        poly.use_smooth=True

    # Place preview variants apart, preserving scale and sculpt silhouette.
    xloc={"ASTEROID_MASSIVE":-3.4,"ASTEROID_SPLIT":0.0,"ASTEROID_RUGGED":3.4}[name]
    rock.location.x=xloc
    rock["variant"]=name
    rock["sculpt_triangles"]=len(rock.data.polygons)

    # Create mobile LODs from the fused sculpt mesh.
    lod0=rock.copy()
    lod0.data=rock.data.copy()
    bpy.context.collection.objects.link(lod0)
    lod0.name="LOD0_"+name
    dec=lod0.modifiers.new("LOD0 triangle budget","DECIMATE")
    dec.ratio=min(.95,400/max(1,len(lod0.data.polygons)))
    bpy.context.view_layer.objects.active=lod0
    bpy.ops.object.modifier_apply(modifier=dec.name)
    lods=[lod0]
    for lodname,target in [("LOD1_"+name,150),("LOD2_"+name,50)]:
        ob=lod0.copy()
        ob.data=lod0.data.copy()
        bpy.context.collection.objects.link(ob)
        ob.name=lodname
        mod=ob.modifiers.new("LOD reduction","DECIMATE")
        mod.ratio=min(.99,target/max(1,len(ob.data.polygons)))
        bpy.context.view_layer.objects.active=ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
        lods.append(ob)
    export_objects.extend(lods)
    variant_info[name]={
        "construction":"fused_metaball_rock_mass_with_sculpted_craters",
        "sculpt_triangles":len(rock.data.polygons),
        "crater_count":crater_count,
        "lod_triangles":{o.name:sum(max(0,len(f.vertices)-2) for f in o.data.polygons) for o in lods}
    }

# Render scene contains the dense sculpt meshes; GLB exports only LODs.
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name.startswith("LOD"):
        ob.hide_render=True
bpy.ops.object.select_all(action="DESELECT")
for ob in export_objects:
    ob.select_set(True)
bpy.context.view_layer.objects.active=export_objects[0]
bpy.ops.export_scene.gltf(filepath=GLB,export_format="GLB",use_selection=True,export_apply=True)
with open(GLB,"rb") as f:
    magic,version,size=struct.unpack("<4sII",f.read(12))
report={
 "revision":"r008",
 "status":"preview_pending_visual_approval",
 "method":"fused irregular rock masses; voxel-remeshed; multi-scale erosion; true crater displacement",
 "glb_bytes":os.path.getsize(GLB),
 "glb_header_valid":magic==b"glTF" and version==2 and size==os.path.getsize(GLB),
 "targets":{"lod0":400,"lod1":150,"lod2":50,"glb_bytes":40960},
 "variants":variant_info
}
json.dump(report,open(QC,"w"),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=OUT+"/asteroid_scene_r008.blend")
print(json.dumps(report,indent=2))
