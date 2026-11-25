import bpy, json, math, os, random, struct
from mathutils import Vector
OUT="build/asteroid"
os.makedirs(OUT,exist_ok=True)
GLB=OUT+"/sd_env_rock_variants_r010.glb"
QC=OUT+"/qc_report_r010.json"

# R010 production preview pass
# Clean scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Export-safe metallic-roughness material: no procedural nodes leave in GLB.
export_mat=bpy.data.materials.new("MAT_asteroid_weathered_iron")
export_mat.diffuse_color=(.075,.068,.058,1)
export_mat.use_nodes=True
ebs=export_mat.node_tree.nodes.get("Principled BSDF")
ebs.inputs["Base Color"].default_value=(.075,.068,.058,1)
ebs.inputs["Metallic"].default_value=.18
ebs.inputs["Roughness"].default_value=.94

# Render-only material: restrained mineral variation, no toy-like high-frequency bump.
render_mat=bpy.data.materials.new("MAT_preview_iron_regolith")
render_mat.diffuse_color=(.055,.052,.047,1)
render_mat.use_nodes=True
rn=render_mat.node_tree.nodes
rl=render_mat.node_tree.links
rbs=rn.get("Principled BSDF")
rbs.inputs["Metallic"].default_value=.16
rbs.inputs["Roughness"].default_value=.96
rnoise=rn.new("ShaderNodeTexNoise")
rnoise.inputs["Scale"].default_value=4.2
rnoise.inputs["Detail"].default_value=5
rnoise.inputs["Roughness"].default_value=.72
rramp=rn.new("ShaderNodeValToRGB")
rramp.color_ramp.elements[0].position=.22
rramp.color_ramp.elements[0].color=(.012,.014,.016,1)
rramp.color_ramp.elements[1].position=.78
rramp.color_ramp.elements[1].color=(.105,.091,.073,1)
mid=rramp.color_ramp.elements.new(.52)
mid.color=(.038,.037,.034,1)
rbump=rn.new("ShaderNodeBump")
rbump.inputs["Strength"].default_value=.24
rbump.inputs["Distance"].default_value=.035
rl.new(rnoise.outputs["Fac"],rramp.inputs["Fac"])
rl.new(rramp.outputs["Color"],rbs.inputs["Base Color"])
rl.new(rnoise.outputs["Fac"],rbump.inputs["Height"])
rl.new(rbump.outputs["Normal"],rbs.inputs["Normal"])

# Irregular, fused rock masses. Metaballs create a genuinely lumpy 3D body,
# rather than a deformed sphere. Crater bowls are sculpted into the fused shell.
variants=[
 ("ASTEROID_MASSIVE", 911, (1.58,1.12,1.03), 11),
 ("ASTEROID_SPLIT",   912, (1.12,1.56,.91), 13),
 ("ASTEROID_RUGGED",  913, (1.42,1.19,1.27), 15),
]
export_objects=[]
variant_info={}
for name,seed,scale,chunks in variants:
    rng=random.Random(seed)
    mb=bpy.data.metaballs.new("META_"+name)
    mb.resolution=.026
    mb.render_resolution=.022
    mb.threshold=.62
    obj=bpy.data.objects.new("META_"+name,mb)
    bpy.context.collection.objects.link(obj)
    # A dominant irregular core plus overlapping lobes of different sizes.
    mb.elements.new().co=(0,0,0)
    mb.elements[0].radius=1.08
    for i in range(chunks):
        az=rng.uniform(0,math.tau)
        z=rng.uniform(-.82,.82)
        rr=math.sqrt(max(.02,1-z*z))*rng.uniform(.48,.98)
        pos=Vector((rr*math.cos(az),rr*math.sin(az),z))*rng.uniform(.62,1.18)
        el=mb.elements.new()
        el.co=pos
        el.radius=rng.uniform(.36,.88)
        el.stiffness=rng.uniform(1.7,2.4)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target="MESH")
    rock=bpy.context.object
    rock.name="SCULPT_"+name
    rock.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

    # Voxel remesh fuses the lobes into one continuous, rough mass.
    rem=rock.modifiers.new("Fused rock surface","REMESH")
    rem.mode="VOXEL"
    rem.voxel_size=.026
    bpy.context.view_layer.objects.active=rock
    bpy.ops.object.modifier_apply(modifier=rem.name)
    smooth=rock.modifiers.new("Very light rock relaxation","SMOOTH")
    smooth.factor=.22
    smooth.iterations=1
    bpy.ops.object.modifier_apply(modifier=smooth.name)

    # Multi-scale displacement: broad fracture planes + small-scale erosion.
    tex=bpy.data.textures.new("erosion_"+name,type="CLOUDS")
    tex.noise_scale=.22
    tex.noise_depth=2
    disp=rock.modifiers.new("Eroded surface","DISPLACE")
    disp.texture=tex
    disp.strength=.105
    disp.mid_level=.52
    bpy.ops.object.modifier_apply(modifier=disp.name)
    tex2=bpy.data.textures.new("pitting_"+name,type="CLOUDS")
    tex2.noise_scale=.075
    tex2.noise_depth=2
    disp2=rock.modifiers.new("Fine pitting","DISPLACE")
    disp2.texture=tex2
    disp2.strength=.035
    disp2.mid_level=.52
    bpy.ops.object.modifier_apply(modifier=disp2.name)

    # Actual crater bowls with raised broken rims, distributed over the body.
    center=rock.location.copy()
    crater_count=8+rng.randrange(6)
    directions=[]
    for j in range(crater_count):
        z=rng.uniform(-.92,.92)
        a=rng.random()*math.tau
        d=Vector((math.sqrt(1-z*z)*math.cos(a),math.sqrt(1-z*z)*math.sin(a),z))
        directions.append((d,rng.uniform(.16,.34),rng.uniform(.10,.24)))
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
        offset+=.008*math.sin(p.x*17+p.y*11)*math.cos(p.z*19)+.004*math.sin(p.x*31-p.z*23)
        v.co += v.normal*offset
    rock.data.update()
    rock.data.materials.append(render_mat)
    for poly in rock.data.polygons:
        poly.use_smooth=False

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
    dec.ratio=min(.95,190/max(1,len(lod0.data.polygons)))
    bpy.context.view_layer.objects.active=lod0
    bpy.ops.object.modifier_apply(modifier=dec.name)
    lods=[lod0]
    for lodname,target in [("LOD1_"+name,135),("LOD2_"+name,45)]:
        ob=lod0.copy()
        ob.data=lod0.data.copy()
        bpy.context.collection.objects.link(ob)
        ob.name=lodname
        mod=ob.modifiers.new("LOD reduction","DECIMATE")
        mod.ratio=min(.99,target/max(1,len(ob.data.polygons)))
        bpy.context.view_layer.objects.active=ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
        lods.append(ob)
    for lod_ob in lods:
        lod_ob.data.materials.clear()
        lod_ob.data.materials.append(export_mat)
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
 "revision":"r010",
 "status":"preview_pending_visual_approval",
 "method":"fused irregular rock masses; broad geological erosion; sculpted impact basins; restrained micro-pitting; export-safe PBR material",
 "glb_bytes":os.path.getsize(GLB),
 "glb_header_valid":magic==b"glTF" and version==2 and size==os.path.getsize(GLB),
 "targets":{"lod0":400,"lod1":150,"lod2":50,"glb_bytes":40960,"export_material_nodes":"principled_only"},
 "variants":variant_info
}
json.dump(report,open(QC,"w"),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=OUT+"/asteroid_scene_r010.blend")
print(json.dumps(report,indent=2))
