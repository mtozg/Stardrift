import bpy
import json
import math
import os
import random
import struct
from mathutils import Vector

random.seed(241124)
OUT = "build/asteroid"
os.makedirs(OUT, exist_ok=True)
GLB = os.path.join(OUT, "sd_env_rock_crystal_r002.glb")
QC = os.path.join(OUT, "qc_report.json")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic, roughness, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    e = p.inputs.get("Emission Color") or p.inputs.get("Emission")
    if e:
        e.default_value = (*color, 1)
    s = p.inputs.get("Emission Strength")
    if s:
        s.default_value = emission
    return m

rock_mat = material("MAT_body", (0.12, 0.105, 0.085), 0.04, 0.96)
# Layered procedural stone: mottled mineral color, fine grain and chipped micro-relief.
nt = rock_mat.node_tree
nodes, links = nt.nodes, nt.links
bsdf = nodes.get("Principled BSDF")
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 19.0
noise.inputs["Detail"].default_value = 5.0
noise.inputs["Roughness"].default_value = 0.82
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.19
ramp.color_ramp.elements[0].color = (0.035, 0.032, 0.028, 1)
ramp.color_ramp.elements[1].position = 0.82
ramp.color_ramp.elements[1].color = (0.24, 0.21, 0.17, 1)
mid = ramp.color_ramp.elements.new(0.51)
mid.color = (0.105, 0.09, 0.072, 1)
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.34
bump.inputs["Distance"].default_value = 0.075
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
crystal_mat = material("MAT_crystal", (0.035, 0.19, 0.20), 0.12, 0.48, 0.015)
amber_mat = material("MAT_mineral", (0.28, 0.105, 0.035), 0.08, 0.72, 0.0)

parts = []
def add_part(obj, mat, name):
    obj.name = name
    obj.data.materials.append(mat)
    parts.append(obj)
    return obj

# Irregular basalt core.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
core = bpy.context.object
core.scale = (1.55, 1.28, 1.12)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
tex = bpy.data.textures.new("TX_rock_silhouette", type="CLOUDS")
tex.noise_scale = 0.23
mod = core.modifiers.new("Silhouette breakup", "DISPLACE")
mod.texture = tex
mod.strength = 0.25
bpy.context.view_layer.objects.active = core
bpy.ops.object.modifier_apply(modifier=mod.name)
add_part(core, rock_mat, "body_core")

def surface(theta, phi, offset):
    x = 1.55 * math.sin(theta) * math.cos(phi)
    y = 1.28 * math.sin(theta) * math.sin(phi)
    z = 1.12 * math.cos(theta)
    n = Vector((x/(1.55**2), y/(1.28**2), z/(1.12**2))).normalized()
    return Vector((x, y, z)) + n * offset, n

# Five small crystal outcrops, each with two to three faceted shards.
shards = 0
for _ in range(5):
    th = random.uniform(0.55, 2.6)
    ph = random.uniform(0, math.tau)
    center, normal = surface(th, ph, -0.015)
    tangent = normal.cross(Vector((0, 0, 1)))
    if tangent.length < 0.01:
        tangent = normal.cross(Vector((0, 1, 0)))
    tangent.normalize()
    bitangent = normal.cross(tangent).normalized()
    for j in range(random.randint(2, 3)):
        angle = random.uniform(0, math.tau)
        direction = tangent * math.cos(angle) + bitangent * math.sin(angle)
        pos = center + direction * random.uniform(0.02, 0.09)
        depth = random.uniform(0.12, 0.23)
        bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=random.uniform(0.035, 0.055),
                                        radius2=0.004, depth=depth,
                                        location=pos + normal * depth * 0.22)
        shard = bpy.context.object
        shard.rotation_mode = "QUATERNION"
        shard.rotation_quaternion = normal.to_track_quat("Z", "Y")
        add_part(shard, crystal_mat, "crystal_shard")
        shards += 1

# Short amber mineral seams as thin low-poly cylinders following surface chords.
veins = 0
for _ in range(5):
    th = random.uniform(0.8, 2.35)
    ph = random.uniform(0, math.tau)
    p1, n1 = surface(th - 0.055, ph - 0.09, 0.002)
    p2, n2 = surface(th + 0.055, ph + 0.09, 0.002)
    vec = p2 - p1
    mid = (p1 + p2) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.007,
                                        depth=vec.length, location=mid)
    vein = bpy.context.object
    vein.rotation_mode = "QUATERNION"
    vein.rotation_quaternion = vec.to_track_quat("Z", "Y")
    add_part(vein, amber_mat, "mineral_vein")
    veins += 1

# Join all detail into one LOD0 mesh; material slots remain explicit.
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = core
bpy.ops.object.join()
lod0 = bpy.context.object
lod0.name = "LOD0_body"

# Create independent decimated LOD meshes for the asset package.
lods = [lod0]
for name, ratio in (("LOD1_body", 0.45), ("LOD2_body", 0.15)):
    dup = lod0.copy()
    dup.data = lod0.data.copy()
    bpy.context.collection.objects.link(dup)
    dup.name = name
    dec = dup.modifiers.new("LOD reduction", "DECIMATE")
    dec.ratio = ratio
    bpy.context.view_layer.objects.active = dup
    bpy.ops.object.modifier_apply(modifier=dec.name)
    lods.append(dup)

# Export all three LOD meshes. This prototype keeps the material palette simple.
bpy.ops.object.select_all(action="DESELECT")
for obj in lods:
    obj.select_set(True)
bpy.context.view_layer.objects.active = lod0
bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB",
                          use_selection=True, export_apply=True)

def tris(obj):
    return sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons)

with open(GLB, "rb") as f:
    magic, version, declared = struct.unpack("<4sII", f.read(12))
report = {
    "asset_id": "env_rock_crystal",
    "revision": "r002",
    "generator": "Blender Python",
    "blender_version": bpy.app.version_string,
    "file": os.path.basename(GLB),
    "glb_bytes": os.path.getsize(GLB),
    "glb_header_valid": magic == b"glTF" and version == 2 and declared == os.path.getsize(GLB),
    "lod_triangles": {obj.name: tris(obj) for obj in lods},
    "material_slots": len(lod0.data.materials),
    "crystal_shards": shards,
    "mineral_veins": veins,
    "target_env_rock_lod0_triangles": 400,
    "target_env_rock_glb_bytes": 40960,
    "status": "prototype_r002_pending_visual_and_mobile_qc"
}
with open(QC, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
