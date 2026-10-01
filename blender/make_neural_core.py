"""
Neural Core — Procedural 3D Model Generator
=============================================

Generates an optimized glTF model of a stylized "neural core" for use in
browser-based augmented reality (MindAR + A-Frame).

Pipeline:
    1. Create a high-poly ico-sphere with cloud-noise displacement (~360K tris)
    2. Add a smooth orbital ring
    3. Apply procedural materials (noise color ramp + metallic ring)
    4. Join meshes and decimate to TARGET_TRIS
    5. UV-unwrap, bake diffuse + normal maps at TEX×TEX resolution
    6. Export as GLB with Draco mesh compression

Usage:
    # Headless (CLI)
    blender --background --python make_neural_core.py

    # Interactive (Blender GUI)
    Open Blender → Scripting tab → Open this file → Run Script

Output:
    ~/neural_core_out/
    ├── neural_core_highpoly.glb   # Uncompressed high-poly reference
    ├── neural_core.glb            # Final optimized model (Draco-compressed)
    ├── core_diffuse.png           # Baked diffuse texture (1024×1024)
    ├── core_normal.png            # Baked normal map (1024×1024)
    └── metrics.json               # Before/after optimization metrics

Configuration:
    TARGET_TRIS : int   — Target triangle count after decimation (default: 10,000)
    TEX         : int   — Baked texture resolution in pixels (default: 1024)
"""

import bpy
import os
import json
import bmesh

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

OUT = os.path.expanduser("~/neural_core_out")
os.makedirs(OUT, exist_ok=True)

TARGET_TRIS = 10_000   # Triangle budget for the decimated model
TEX = 1024             # Baked texture resolution (width & height in pixels)

# ──────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────────────────────────────────────

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def tris(obj):
    """Return the triangle count for a mesh object."""
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def size_mb(path):
    """Return the file size in megabytes."""
    return os.path.getsize(path) / 1_048_576


# ──────────────────────────────────────────────────────────────────────────────
# Step 1 — High-Poly Source Geometry
# ──────────────────────────────────────────────────────────────────────────────

# Core sphere: high-subdivision ico-sphere with cloud-noise displacement
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=8, radius=1)
core = bpy.context.active_object
core.name = "core_high"

tex = bpy.data.textures.new("clouds", "CLOUDS")
tex.noise_scale = 0.6
tex.noise_depth = 4

disp = core.modifiers.new("disp", "DISPLACE")
disp.texture = tex
disp.strength = 0.28
disp.mid_level = 0.5
bpy.ops.object.modifier_apply(modifier="disp")
bpy.ops.object.shade_smooth()

# Orbital ring: thin torus tilted at an angle
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.55, minor_radius=0.05,
    major_segments=256, minor_segments=64,
)
ring = bpy.context.active_object
ring.rotation_euler = (1.2, 0.2, 0)
ring.name = "ring_high"
bpy.ops.object.shade_smooth()

# ──────────────────────────────────────────────────────────────────────────────
# Step 2 — Procedural Materials
# ──────────────────────────────────────────────────────────────────────────────


def make_core_material():
    """Create the core's procedural material (noise-driven blue/cyan ramp)."""
    mat = bpy.data.materials.new("core_mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 6

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.02, 0.05, 0.12, 1)  # Deep navy
    ramp.color_ramp.elements[1].color = (0.1, 0.8, 1.0, 1)     # Bright cyan

    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])
    return mat


core.data.materials.append(make_core_material())

# Ring material: near-white metallic
ring_mat = bpy.data.materials.new("ring_mat")
ring_mat.use_nodes = True
ring_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.95, 0.95, 0.95, 1)
ring.data.materials.append(ring_mat)

# ──────────────────────────────────────────────────────────────────────────────
# Step 3 — Join Meshes & Record "Before" Metrics
# ──────────────────────────────────────────────────────────────────────────────

bpy.ops.object.select_all(action="DESELECT")
core.select_set(True)
ring.select_set(True)
bpy.context.view_layer.objects.active = core
bpy.ops.object.join()

high = core
high.name = "neural_core_high"

tri_before = tris(high)
dc_before = len(high.data.materials)

# Export uncompressed high-poly reference
bpy.ops.object.select_all(action="DESELECT")
high.select_set(True)
before_path = os.path.join(OUT, "neural_core_highpoly.glb")
bpy.ops.export_scene.gltf(
    filepath=before_path,
    export_format="GLB",
    use_selection=True,
    export_draco_mesh_compression_enable=False,
)

# ──────────────────────────────────────────────────────────────────────────────
# Step 4 — Decimate to Target Triangle Count
# ──────────────────────────────────────────────────────────────────────────────

low = high.copy()
low.data = high.data.copy()
low.name = "neural_core_low"
sc.collection.objects.link(low)

bpy.ops.object.select_all(action="DESELECT")
low.select_set(True)
bpy.context.view_layer.objects.active = low

# Triangulate first, then collapse-decimate
tri_mod = low.modifiers.new("tri", "TRIANGULATE")
bpy.ops.object.modifier_apply(modifier="tri")

dec_mod = low.modifiers.new("dec", "DECIMATE")
dec_mod.decimate_type = "COLLAPSE"
dec_mod.ratio = TARGET_TRIS / tris(low)
bpy.ops.object.modifier_apply(modifier="dec")

# Clean up materials and re-UV for baking
low.data.materials.clear()
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.shade_smooth()

# ──────────────────────────────────────────────────────────────────────────────
# Step 5 — Bake Textures (Diffuse + Normal)
# ──────────────────────────────────────────────────────────────────────────────

bake_mat = bpy.data.materials.new("baked")
bake_mat.use_nodes = True
low.data.materials.append(bake_mat)
nodes = bake_mat.node_tree.nodes

# Configure Cycles for baking
sc.render.engine = "CYCLES"
sc.cycles.samples = 16
sc.cycles.device = "CPU"

bake = sc.render.bake
bake.use_selected_to_active = True
bake.cage_extrusion = 0.06
bake.margin = 8


def bake_pass(kind, name, is_srgb):
    """Bake a single texture pass from the high-poly to the low-poly mesh.

    Args:
        kind:     Blender bake type ('DIFFUSE', 'NORMAL', etc.)
        name:     Output filename (without extension)
        is_srgb:  Whether the image should use sRGB color space
    """
    img = bpy.data.images.new(name, TEX, TEX)
    img.colorspace_settings.name = "sRGB" if is_srgb else "Non-Color"

    node = nodes.new("ShaderNodeTexImage")
    node.image = img
    nodes.active = node

    bpy.ops.object.select_all(action="DESELECT")
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low

    if kind == "DIFFUSE":
        bake.use_pass_direct = False
        bake.use_pass_indirect = False
        bake.use_pass_color = True

    bpy.ops.object.bake(type=kind)

    img.filepath_raw = os.path.join(OUT, name + ".png")
    img.file_format = "PNG"
    img.save()
    img.pack()
    return node


diffuse_node = bake_pass("DIFFUSE", "core_diffuse", is_srgb=True)
normal_node = bake_pass("NORMAL", "core_normal", is_srgb=False)

# Wire baked textures into the Principled BSDF
principled = nodes["Principled BSDF"]
links = bake_mat.node_tree.links
normal_map = nodes.new("ShaderNodeNormalMap")

links.new(diffuse_node.outputs["Color"], principled.inputs["Base Color"])
links.new(normal_node.outputs["Color"], normal_map.inputs["Color"])
links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
principled.inputs["Roughness"].default_value = 0.6

# ──────────────────────────────────────────────────────────────────────────────
# Step 6 — Export Optimized Model (Draco-Compressed GLB)
# ──────────────────────────────────────────────────────────────────────────────

bpy.data.objects.remove(high, do_unlink=True)

bpy.ops.object.select_all(action="DESELECT")
low.select_set(True)
bpy.context.view_layer.objects.active = low

after_path = os.path.join(OUT, "neural_core.glb")
bpy.ops.export_scene.gltf(
    filepath=after_path,
    export_format="GLB",
    use_selection=True,
    export_image_format="JPEG",
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14,
    export_draco_normal_quantization=10,
    export_draco_texcoord_quantization=12,
)

# ──────────────────────────────────────────────────────────────────────────────
# Step 7 — Output Metrics
# ──────────────────────────────────────────────────────────────────────────────

tri_after = tris(low)
mb_before = size_mb(before_path)
mb_after = size_mb(after_path)

metrics = {
    "tri_before": f"{tri_before:,}",
    "tri_after": f"{tri_after:,}",
    "tri_change": f"-{100 * (1 - tri_after / tri_before):.1f}%",
    "dc_before": dc_before,
    "dc_after": 1,
    "dc_change": f"-{dc_before - 1}",
    "mb_before": f"{mb_before:.2f}",
    "mb_after": f"{mb_after:.2f}",
    "mb_change": f"-{100 * (1 - mb_after / mb_before):.1f}%",
}

metrics_path = os.path.join(OUT, "metrics.json")
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print("\n" + "=" * 50)
print("  Neural Core — Build Complete")
print("=" * 50)
print(f"  Output directory : {OUT}")
print(f"  Triangles        : {tri_before:,} → {tri_after:,}")
print(f"  File size        : {mb_before:.2f} MB → {mb_after:.2f} MB")
print("=" * 50 + "\n")
