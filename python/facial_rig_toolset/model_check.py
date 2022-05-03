import os
from functools import partial
import pprint

from maya import mel
import maya.cmds as mc


MATERIAL_PARMS = {
    "skin": {
        "color": [0.734, 0.498327, 0.404434],
        "specularRollOff": 0.4,
        "reflectivity": 0.3,
        "eccentricity": 0.2
    },
    "hair": {
        "color": [0.107, 0.0757544, 0.058957],
        "specularRollOff": 0,
        "reflectivity": 0,
        "eccentricity": 0
    },
    "lips": {
        "color": [0.4398, 0.1724, 0.1724],
        "specularRollOff": 0.4,
        "reflectivity": 0.3,
        "eccentricity": 0.2
    },
    "brows": {
        "color": [0.107, 0.0757544, 0.058957],
        "specularRollOff": 0,
        "reflectivity": 0,
        "eccentricity": 0
    },
    "mustache": {
        "color": [0.107, 0.0757544, 0.058957],
        "specularRollOff": 0,
        "reflectivity": 0,
        "eccentricity": 0
    },
    "tongue": {
        "color": [0.702, 0.211302, 0.211302],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
    "teeth": {
        "color": [1, 1, 1],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
    "gums": {
        "color": [0.702, 0.332748, 0.332748],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
    "inner_mouth": {
        "color": [0.702, 0.398736, 0.398736],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
    "lashes": {
        "color": [0.107, 0.0757544, 0.058957],
        "specularRollOff": 0,
        "reflectivity": 0,
        "eccentricity": 0
    },
    "eyeball": {
        "color": [1, 1, 1],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
    "sclera": {
        "color": [1, 1, 1],
        "transparency": [1, 1, 1],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
    "pupil": {
        "color": [0, 0, 0],
        "specularRollOff": 0,
        "reflectivity": 0,
        "eccentricity": 0
    },
    "inner_iris": {
        "color": [0.062, 0.0426, 0.0322],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
    "iris": {
        "color": [0.127, 0.0789647, 0.053213],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
    "outer_iris": {
        "color": [0.062, 0.0426, 0.0322],
        "specularRollOff": 1,
        "reflectivity": 1,
        "eccentricity": 0.2
    },
}


def zero_out_pivots():

    models_selected = mc.ls(selection=True, type='transform')

    mc.xform(models_selected, piv=(0, 0, 0), ws=True)


def fix_character_scale_and_zero_out_pivots(model_height_target=175):
    '''
    fix the character scale and zero out the pivots

    it works only if the character has a body
    as the script calculates the bounding box for the whole character from the feet to the head

    for only head the calculations will be incorrect as the head is the fifth part of the body
    but will be considered as the whole
    '''
    models_selected = mc.ls(selection=True, type='transform')

    if not models_selected:
        print("Please, select the model")

    bbox = mc.exactWorldBoundingBox(models_selected)

    bb_min_y = bbox[1]
    bb_max_y = bbox[4]

    model_height = bb_max_y - bb_min_y
    scale_ratio = model_height_target / model_height

    mc.move(-bb_min_y, models_selected, y=True, ws=True, r=True)

    mc.xform(models_selected, piv=(0, 0, 0), ws=True)
    mc.scale(scale_ratio, scale_ratio, scale_ratio,
             models_selected, ws=True, r=True)


def auto_uvs():
    '''
    set Automatic UVs
    '''
    models_selected = mc.ls(selection=True, type='transform')

    if not models_selected:
        print("Please, select the model")

    for model in models_selected:
        mc.polyAutoProjection(f"{model}.f[*]")


def soften_edges():
    '''
    soften Edges
    '''
    models_selected = mc.ls(selection=True, type='transform')

    if not models_selected:
        print("Please, select the model")

    for model in models_selected:
        mc.polySoftEdge(model, angle=180)



def freeze_tranfsorm():
    '''
    freeze transformation
    '''
    models_selected = mc.ls(selection=True, type='transform')

    if not models_selected:
        print("Please, select the model")

    for model in models_selected:
        mc.makeIdentity(model, apply=True, t=1, r=1, s=1, n=0, pn=1)


def delete_history():
    '''
    delete history
    '''
    models_selected = mc.ls(selection=True, type='transform')

    if not models_selected:
        print("Please, select the model")

    mc.delete(models_selected, ch=True)


def check_symmetry():
    '''
    check symmetry
    '''
    symmetry_script_path = os.path.join(
        os.path.dirname(__file__), 'mel', 'symmetry.mel')

    symmetry_script_path = os.path.normpath(symmetry_script_path)
    symmetry_script_path = symmetry_script_path.replace('\\', '\\\\')

    mel.eval(f'source "{symmetry_script_path}"')


def delete_intermediate_objects():
    '''
    delete shapeOrig and shapeDeformed
    '''
    models_selected = mc.ls(selection=True, type='transform')

    if not models_selected:
        print("Please, select the model")

    for model in models_selected:
        # get all the transforms in hierarchy
        transforms = mc.ls(model, mc.listRelatives(
            model, ad=1, type='transform'))
        for transform in transforms:
            # get the shapes of transform
            model_shapes = mc.listRelatives(transform, s=1)
            # do not delete if there is only one shape node
            if len(model_shapes) > 1:
                for model_shape in model_shapes:
                    # if nothing is connected to the shape node, delete it
                    if mc.getAttr(f"{model_shape}.intermediateObject"):
                        mc.delete(model_shape)


def delete_display_and_render_layers():
    '''
    delete the render and display layers
    '''
    display_layers = mc.ls(type='displayLayer')
    render_layers = mc.ls(type='renderLayer')

    for display_layer in display_layers:
        if len(display_layers) > 1 and display_layer != "defaultLayer":
            mc.delete(display_layer)

    for render_layer in render_layers:
        if len(render_layers) > 1 and render_layer != "defaultLayer":
            mc.delete(render_layer)


def delete_unknown_nodes():
    '''
    delete unknown nodes
    '''
    unknown_nodes = mc.ls(type = "unknown")

    for unknown_node in unknown_nodes:
        
        if mc.objExists(unknown_node):
            mc.delete(unknown_node)


def delete_unused_nodes():
    '''
    delete unused nodes in hypershade
    '''
    mel.eval("MLdeleteUnused")


def set_material(material_type, material_parms):
    '''
    assignment material (AnimColors)
    '''
    faces = mc.ls(selection=True)
    shader = f"{material_type}_mat"
    sg = f"{material_type}_sg"
    
    if not mc.ls(sg): 
    
        shader = mc.shadingNode("blinn", asShader=True, name=shader )
        sg = mc.sets(empty=True, renderable=True, noSurfaceShader=True,  name=sg)
        mc.connectAttr( f"{shader}.outColor", f"{sg}.surfaceShader", f=True) 
      
    mc.sets(faces, e=True, forceElement=sg)
    
    for attr, value in material_parms.items():
        # checking the type of the object
        if isinstance(value, list):
            mc.setAttr(f"{shader}.{attr}", *value, type="double3")
        else:
            mc.setAttr(f"{shader}.{attr}", value)


def check_current_unit():
    '''
    set current units to cm
    '''
    if mc.currentUnit(query=True, linear=True) != 'cm':
        mc.currentUnit(linear='cm')