"""
Virtual Reality Spring 2026
Project 1 course-provided implementation file

Mufeng Zhu (TA), Spring 2025

Revised for Spring 2026 offering
"""

# A simple script that uses blender to render views of a single object by rotation the camera around it.
# Also produces depth map at the same time.

import argparse, sys, os
import json
import bpy
import mathutils
import numpy as np

# Changed to my netid
np.random.seed(120) 

DEBUG = False

VIEWS = 50
RESOLUTION = 800

RESULTS_PATH = 'step1_rgbd_data'

COLOR_BITS = 8
DEPTH_BITS = 16
FORMAT = 'PNG'
RANDOM_VIEWS = True
UPPER_VIEWS = True

fp = bpy.path.abspath(f"//{RESULTS_PATH}")

def listify_matrix(matrix):
    matrix_list = []
    for row in matrix:
        matrix_list.append(list(row))
    return matrix_list


if not os.path.exists(fp):
    os.makedirs(fp)

# Data to store in JSON file
out_data = {
    'camera_angle_x': bpy.data.objects['Camera'].data.angle_x,
}

# Render Optimizations
bpy.context.scene.render.use_persistent_data = True

# Set up rendering of depth map.
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links

# Add passes for additionally dumping albedo and normals.
bpy.context.scene.view_layers["RenderLayer"].use_pass_normal = True
bpy.context.scene.render.image_settings.file_format = str(FORMAT)
bpy.context.scene.render.image_settings.color_depth = str(COLOR_BITS)
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

if 'Custom Outputs' not in tree.nodes:
    # Create input render layer node.
    render_layers = tree.nodes.new('CompositorNodeRLayers')
    render_layers.label = 'Custom Outputs'
    render_layers.name = 'Custom Outputs'

    depth_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
    depth_file_output.label = 'Depth Output'
    depth_file_output.name = 'Depth Output'
    depth_file_output.format.file_format = 'PNG'
    depth_file_output.format.color_depth = str(DEPTH_BITS)
    
    if FORMAT == 'OPEN_EXR':
        links.new(render_layers.outputs['Depth'], depth_file_output.inputs[0])
    else:
        # Remap as other types can not represent the full range of depth.
        map = tree.nodes.new(type="CompositorNodeMapRange")
        map.inputs['From Min'].default_value = 0
        map.inputs['From Max'].default_value = 8
        map.inputs['To Min'].default_value = 1
        map.inputs['To Max'].default_value = 0
        links.new(render_layers.outputs['Depth'], map.inputs[0])

        links.new(map.outputs[0], depth_file_output.inputs[0])

    # normal_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
    # normal_file_output.label = 'Normal Output'
    # normal_file_output.name = 'Normal Output'
    # links.new(render_layers.outputs['Normal'], normal_file_output.inputs[0])

# Background
bpy.context.scene.render.dither_intensity = 0.0
bpy.context.scene.render.film_transparent = True

# Create collection for objects not to render with background


def parent_obj_to_camera(b_camera):
    origin = (0, 0, 0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    b_camera.parent = b_empty  # setup parenting

    scn = bpy.context.scene
    scn.collection.objects.link(b_empty)
    bpy.context.view_layer.objects.active = b_empty
    # scn.objects.active = b_empty
    return b_empty


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

from math import radians

stepsize = 360.0 / VIEWS
rotation_mode = 'XYZ'

if not DEBUG:
    # for output_node in [depth_file_output, normal_file_output]:
    for output_node in [depth_file_output]:
        output_node.base_path = ''

out_data['frames'] = []

for i in range(0, VIEWS):
    # Set the file path for the main rendering result
    scene.render.filepath = os.path.join(fp, f"r_{i}")

    if RANDOM_VIEWS:
        if UPPER_VIEWS:
            rot = np.random.uniform(0, 1, size=3) * (1, 0, 2 * np.pi)
            rot[0] = np.abs(np.arccos(1 - 2 * rot[0]) - np.pi / 2)
            b_empty.rotation_euler = rot
        else:
            b_empty.rotation_euler = np.random.uniform(0, 2 * np.pi, size=3)
    else:
        print(f"Rotation {stepsize * i}, {radians(stepsize * i)}")
        b_empty.rotation_euler[2] += radians(stepsize)

    depth_file_output.base_path = fp
    depth_file_output.file_slots[0].path = f"r_{i}_depth_"

    # normal_file_output.base_path = fp
    # normal_file_output.file_slots[0].path = f"r_{i}_normal_"
    # Render and save files
    if DEBUG:
        break
    else:
        bpy.ops.render.render(write_still=True)


    frame_data = {
        'file_path': scene.render.filepath + '.png',
        'rotation': radians(stepsize),
        'transform_matrix': listify_matrix(cam.matrix_world)
    }
    out_data['frames'].append(frame_data)


if not DEBUG:
    with open(fp + '/' + 'transforms.json', 'w') as out_file:
        json.dump(out_data, out_file, indent=4)
