"""
Virtual Reality Spring 2026
Project 1 course-provided implementation file

Mufeng Zhu (TA), Spring 2025

Revised for Spring 2026 offering
"""


import bpy
import math
import argparse, sys, os
import json
import mathutils
import numpy as np
from math import radians


def initialization(mesh_path):
    # Remove default cube and other meshes
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete()

    bpy.ops.wm.ply_import(filepath = mesh_path)  # import PLY
    model = bpy.context.active_object
    model.rotation_euler = (0, 0, 0)
    model.select_set(True)

    # assign material
    mat = bpy.data.materials.new(name="test")
    model.data.materials.append(mat)
    mat.use_nodes = True
    mat.node_tree.nodes.new(type="ShaderNodeAttribute")
    mat.node_tree.nodes["Attribute"].attribute_name = "Col"
    diffuse = mat.node_tree.nodes.new(type='ShaderNodeBsdfDiffuse')
    input = diffuse.inputs["Color"]
    output = mat.node_tree.nodes["Attribute"].outputs["Color"]
    mat.node_tree.links.new(input, output)

    right = mat.node_tree.nodes['Material Output'].inputs['Surface']
    left = diffuse.outputs[0]
    mat.node_tree.links.new(left, right)


    bpy.ops.node.new_geometry_nodes_modifier()
    node_group = bpy.context.object.modifiers[0].node_group
    nodes = node_group.nodes
    cube = nodes.new(type="GeometryNodeMeshCube")
    nodes['Cube'].inputs[0].default_value = (0.01, 0.01, 0.01)
    set_material = nodes.new(type="GeometryNodeSetMaterial")
    set_material.inputs[2].default_value = mat
    IoP = nodes.new(type="GeometryNodeInstanceOnPoints")
    RI = nodes.new(type="GeometryNodeRealizeInstances")
    link_left = nodes["Group Input"].outputs["Geometry"]
    link_right = IoP.inputs["Points"]
    links = node_group.links
    links.new(link_left, link_right)

    link_left = IoP.outputs[0]
    link_right = RI.inputs[0]
    links.new(link_left, link_right)

    link_left = RI.outputs[0]
    link_right = nodes["Group Output"].inputs[0]
    links.new(link_left, link_right)

    link_left = cube.outputs["Mesh"]
    link_right = set_material.inputs["Geometry"]
    links.new(link_left, link_right)

    link_left = set_material.outputs[0]
    link_right = IoP.inputs["Instance"]
    links.new(link_left, link_right)


def parent_obj_to_camera(b_camera):
    origin = (0, 0, 0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    b_camera.parent = b_empty  # setup parenting

    scn = bpy.context.scene
    scn.collection.objects.link(b_empty)
    bpy.context.view_layer.objects.active = b_empty
    return b_empty


def listify_matrix(matrix):
    matrix_list = []
    for row in matrix:
        matrix_list.append(list(row))
    return matrix_list





DEBUG = False

RESOLUTION = 800
COLOR_BITS = 8
FORMAT = 'PNG'

argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]  # get all args after "--"
else:
    argv = []

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, default='reconstructed.ply', help='Input PLY file')
parser.add_argument('--output', type=str, default='images/step3', help='Output directory')
args = parser.parse_known_args(argv)[0]

RESULTS_PATH = args.output
fp = bpy.path.abspath(f"//{RESULTS_PATH}")

if not os.path.exists(fp):
    os.makedirs(fp)

file_path = args.input
initialization(file_path)
out_data = {
    'camera_angle_x': bpy.data.objects['Camera'].data.angle_x,
}

bpy.context.scene.render.use_persistent_data = True

# Set up rendering of depth map.
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links

# Add passes for additionally dumping albedo and normals.
# bpy.context.scene.view_layers["RenderLayer"].use_pass_normal = True
vl_name = "RenderLayer" if "RenderLayer" in bpy.context.scene.view_layers else "ViewLayer"
bpy.context.scene.view_layers[vl_name].use_pass_diffuse_color = True
bpy.context.scene.view_layers[vl_name].use_pass_diffuse_direct = False
bpy.context.scene.view_layers[vl_name].use_pass_diffuse_indirect = False
bpy.context.scene.render.image_settings.file_format = str(FORMAT)
bpy.context.scene.render.image_settings.color_depth = str(COLOR_BITS)

if not DEBUG:
    # Create input render layer node.
    render_layers = tree.nodes.new('CompositorNodeRLayers')
    tree.nodes.new('CompositorNodeComposite')
    left = tree.nodes['Render Layers'].outputs['DiffCol']

    tree.nodes.new('CompositorNodeSetAlpha')
    tree.nodes['Set Alpha'].mode = 'APPLY'

    right = tree.nodes['Set Alpha'].inputs['Image']
    tree.links.new(left, right)

    left = tree.nodes['Render Layers'].outputs['Alpha']
    right = tree.nodes['Set Alpha'].inputs['Alpha']
    tree.links.new(left, right)

    left = tree.nodes['Set Alpha'].outputs['Image']
    right = tree.nodes['Composite'].inputs['Image']
    tree.links.new(left, right)


# Background
bpy.context.scene.render.dither_intensity = 0.0
bpy.context.scene.render.film_transparent = True

# Create collection for objects not to render with background
scene = bpy.context.scene
scene.render.resolution_x = RESOLUTION
scene.render.resolution_y = RESOLUTION
scene.render.resolution_percentage = 100

cam = scene.objects['Camera']

cam.location = (0, 4.0, 0.5)
cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'
b_empty = parent_obj_to_camera(cam)
cam_constraint.target = b_empty

scene.render.image_settings.file_format = 'PNG'  # set output format to .png


# Load transforms.json
with open(os.path.join("step1_rgbd_data", "transforms.json"), 'r') as f:
    transforms = json.load(f)

for frame in transforms['frames']:
    file_path = frame['file_path']
    basename = os.path.basename(file_path)

    # Set output path
    scene.render.filepath = os.path.join(fp, basename.replace(".png", ""))

    # Set camera pose
    matrix = mathutils.Matrix(frame['transform_matrix'])
    cam.matrix_world = matrix

    if not DEBUG:
        if not os.path.exists(scene.render.filepath + ".png"):
            bpy.ops.render.render(write_still=True)
        else:
            print(f"Skipping {scene.render.filepath}, already exists.")

