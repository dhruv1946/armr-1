# Run:  blender --background --python make_neural_core.py
# or paste in Blender > Scripting tab > Run Script. Output: ~/neural_core_out/
import bpy, os, json, bmesh

OUT = os.path.expanduser("~/neural_core_out"); os.makedirs(OUT, exist_ok=True)
TARGET_TRIS, TEX = 10000, 1024

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def tris(o):
    me = o.data; me.calc_loop_triangles(); return len(me.loop_triangles)

def size_mb(p): return os.path.getsize(p) / 1048576

# ---------- high-poly source ----------
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=8, radius=1)
core = bpy.context.active_object; core.name = "core_high"
tex = bpy.data.textures.new("clouds", 'CLOUDS'); tex.noise_scale = 0.6; tex.noise_depth = 4
d = core.modifiers.new("disp", 'DISPLACE'); d.texture = tex; d.strength = 0.28; d.mid_level = 0.5
bpy.ops.object.modifier_apply(modifier="disp")
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_torus_add(major_radius=1.55, minor_radius=0.05, major_segments=256, minor_segments=64)
ring = bpy.context.active_object; ring.rotation_euler = (1.2, 0.2, 0); ring.name = "ring_high"
bpy.ops.object.shade_smooth()

def mat_core():
    m = bpy.data.materials.new("core_mat"); m.use_nodes = True; n = m.node_tree.nodes; l = m.node_tree.links
    nt = n.new("ShaderNodeTexNoise"); nt.inputs["Scale"].default_value = 6
    cr = n.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (0.02, 0.05, 0.12, 1); cr.color_ramp.elements[1].color = (0.1, 0.8, 1.0, 1)
    l.new(nt.outputs["Fac"], cr.inputs["Fac"]); l.new(cr.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
    return m
core.data.materials.append(mat_core())
rm = bpy.data.materials.new("ring_mat"); rm.use_nodes = True
rm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.95, 0.95, 0.95, 1)
ring.data.materials.append(rm)

bpy.ops.object.select_all(action='DESELECT'); core.select_set(True); ring.select_set(True)
bpy.context.view_layer.objects.active = core; bpy.ops.object.join()
high = core; high.name = "neural_core_high"
tri_before = tris(high); dc_before = len(high.data.materials)

# ---------- export "before" (uncompressed) ----------
bpy.ops.object.select_all(action='DESELECT'); high.select_set(True)
before_path = os.path.join(OUT, "neural_core_highpoly.glb")
bpy.ops.export_scene.gltf(filepath=before_path, export_format='GLB', use_selection=True, export_draco_mesh_compression_enable=False)

# ---------- decimate ----------
low = high.copy(); low.data = high.data.copy(); low.name = "neural_core_low"; sc.collection.objects.link(low)
bpy.ops.object.select_all(action='DESELECT'); low.select_set(True); bpy.context.view_layer.objects.active = low
tr = low.modifiers.new("tri", 'TRIANGULATE'); bpy.ops.object.modifier_apply(modifier="tri")
dm = low.modifiers.new("dec", 'DECIMATE'); dm.decimate_type = 'COLLAPSE'; dm.ratio = TARGET_TRIS / tris(low)
bpy.ops.object.modifier_apply(modifier="dec")
low.data.materials.clear()
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02); bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_smooth()

# ---------- bake ----------
bake_mat = bpy.data.materials.new("baked"); bake_mat.use_nodes = True; low.data.materials.append(bake_mat)
nodes = bake_mat.node_tree.nodes
sc.render.engine = 'CYCLES'; sc.cycles.samples = 16; sc.cycles.device = 'CPU'
b = sc.render.bake; b.use_selected_to_active = True; b.cage_extrusion = 0.06; b.margin = 8
def bake(kind, name, srgb):
    img = bpy.data.images.new(name, TEX, TEX); img.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
    node = nodes.new("ShaderNodeTexImage"); node.image = img; nodes.active = node
    bpy.ops.object.select_all(action='DESELECT'); high.select_set(True); low.select_set(True); bpy.context.view_layer.objects.active = low
    if kind == 'DIFFUSE': b.use_pass_direct = False; b.use_pass_indirect = False; b.use_pass_color = True
    bpy.ops.object.bake(type=kind)
    img.filepath_raw = os.path.join(OUT, name + ".png"); img.file_format = 'PNG'; img.save(); img.pack()
    return node
dn = bake('DIFFUSE', "core_diffuse", True)
nn = bake('NORMAL', "core_normal", False)
pb = nodes["Principled BSDF"]; lk = bake_mat.node_tree.links
nm = nodes.new("ShaderNodeNormalMap")
lk.new(dn.outputs["Color"], pb.inputs["Base Color"]); lk.new(nn.outputs["Color"], nm.inputs["Color"]); lk.new(nm.outputs["Normal"], pb.inputs["Normal"])
pb.inputs["Roughness"].default_value = 0.6

# ---------- export "after" (Draco) ----------
bpy.data.objects.remove(high, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT'); low.select_set(True); bpy.context.view_layer.objects.active = low
after_path = os.path.join(OUT, "neural_core.glb")
bpy.ops.export_scene.gltf(filepath=after_path, export_format='GLB', use_selection=True, export_image_format='JPEG',
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12)

tri_after = tris(low); mb_b = size_mb(before_path); mb_a = size_mb(after_path)
m = {"tri_before": f"{tri_before:,}", "tri_after": f"{tri_after:,}", "tri_change": f"-{100*(1-tri_after/tri_before):.1f}%",
     "dc_before": dc_before, "dc_after": 1, "dc_change": f"-{dc_before-1}",
     "mb_before": f"{mb_b:.2f}", "mb_after": f"{mb_a:.2f}", "mb_change": f"-{100*(1-mb_a/mb_b):.1f}%"}
json.dump(m, open(os.path.join(OUT, "metrics.json"), "w"), indent=2)
print("\n===== SEND THIS TO CLAUDE =====\n" + json.dumps(m, indent=2) + "\n===============================")
