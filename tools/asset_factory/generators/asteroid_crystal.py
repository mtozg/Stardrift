import bpy,json,math,os,random,struct
from mathutils import Vector
OUT="build/asteroid";os.makedirs(OUT,exist_ok=True)
GLB=OUT+"/sd_env_rock_variants_r007.glb";QC=OUT+"/qc_report_r007.json"
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
m=bpy.data.materials.new("MAT_body");m.use_nodes=True
n=m.node_tree.nodes;l=m.node_tree.links;p=n.get("Principled BSDF");p.inputs["Metallic"].default_value=.08;p.inputs["Roughness"].default_value=.94
t=n.new("ShaderNodeTexNoise");t.inputs["Scale"].default_value=6;t.inputs["Detail"].default_value=8
r=n.new("ShaderNodeValToRGB");r.color_ramp.elements[0].color=(.012,.013,.015,1);r.color_ramp.elements[1].color=(.24,.22,.19,1)
b=n.new("ShaderNodeBump");b.inputs["Strength"].default_value=.55;b.inputs["Distance"].default_value=.085
l.new(t.outputs["Fac"],r.inputs["Fac"]);l.new(r.outputs["Color"],p.inputs["Base Color"]);l.new(t.outputs["Fac"],b.inputs["Height"]);l.new(b.outputs["Normal"],p.inputs["Normal"])
variants=[("ASTEROID_FLAT",(1.4,1.1,.78),20,701,.15),("ASTEROID_ELONGATED",(1.58,.88,.98),17,702,.17),("ASTEROID_JAGGED",(1.22,1.08,1.13),24,703,.23)]
alllod=[];qc={}
for name,sc,count,seed,amp in variants:
 rng=random.Random(seed);cr=[]
 for i in range(count):
  z=rng.uniform(-.9,.9);a=rng.random()*math.tau;d=Vector((math.sqrt(1-z*z)*math.cos(a),math.sqrt(1-z*z)*math.sin(a),z));cr.append((d,rng.uniform(.07,.20),rng.uniform(.06,.14)))
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5,radius=1);hi=bpy.context.object;hi.name="SCULPT_"+name
 for v in hi.data.vertices:
  d=v.co.normalized();q=1+amp*(.5*math.sin(d.x*8+seed*.01)*math.sin(d.y*7)*math.cos(d.z*8)+.25*math.sin(d.x*19+d.z*13)*math.cos(d.y*17))
  for c,rad,dep in cr:
   x=math.acos(max(-1,min(1,d.dot(c))))/rad
   if x<1.8:q+=-dep*math.exp(-((x/.66)**2)*2)+dep*.36*math.exp(-(((x-1.02)/.17)**2))+dep*.06*math.sin(x*25+seed)*math.exp(-((x-1)/.3)**2)
  q+=amp*.08*math.sin(d.x*53+d.y*47+d.z*39);v.co=(d.x*sc[0]*q,d.y*sc[1]*q,d.z*sc[2]*q)
 hi.data.update();hi.data.materials.append(m)
 for f in hi.data.polygons:f.use_smooth=True
 low=hi.copy();low.data=hi.data.copy();bpy.context.collection.objects.link(low);low.name="LOD0_"+name
 mod=low.modifiers.new("LOD0 budget","DECIMATE");mod.ratio=.038;bpy.context.view_layer.objects.active=low;bpy.ops.object.modifier_apply(modifier=mod.name)
 lod=[low]
 for nm,ratio in [("LOD1_"+name,.46),("LOD2_"+name,.155)]:
  ob=low.copy();ob.data=low.data.copy();bpy.context.collection.objects.link(ob);ob.name=nm;md=ob.modifiers.new("LOD reduction","DECIMATE");md.ratio=ratio;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=md.name);lod.append(ob)
 alllod+=lod
 qc[name]={"craters":count,"sculpt_triangles":len(hi.data.polygons),"lod_triangles":{o.name:sum(max(0,len(f.vertices)-2) for f in o.data.polygons) for o in lod}}
bpy.ops.object.select_all(action="DESELECT")
for o in alllod:o.select_set(True)
bpy.context.view_layer.objects.active=alllod[0];bpy.ops.export_scene.gltf(filepath=GLB,export_format="GLB",use_selection=True,export_apply=True)
with open(GLB,"rb") as f:magic,ver,size=struct.unpack("<4sII",f.read(12))
report={"revision":"r007","status":"crater_sculpt_preview_pending_visual_approval","glb_bytes":os.path.getsize(GLB),"glb_header_valid":magic==b"glTF" and ver==2 and size==os.path.getsize(GLB),"targets":{"lod0":400,"lod1":150,"lod2":50,"glb_bytes":40960},"variants":qc}
json.dump(report,open(QC,"w"),indent=2);bpy.ops.wm.save_as_mainfile(filepath=OUT+"/asteroid_scene_r007.blend");print(json.dumps(report,indent=2))
