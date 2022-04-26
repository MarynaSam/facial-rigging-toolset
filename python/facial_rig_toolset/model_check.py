import os
from functools import partial
import pprint

from maya import mel
import maya.cmds as mc

model_height_target = 175
models_selected = []
bboxes = {}
material_parms = {
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


# fix the character scale and zero out the pivots

def fix_character_scale_and_zero_out_pivots():

    bbox = mc.exactWorldBoundingBox(models_selected)

    bb_min_y = bbox[1]
    bb_max_y = bbox[4]

    model_height = bb_max_y - bb_min_y
    scale_ratio = model_height_target / model_height

    mc.move(-bb_min_y, models_selected, y=True, ws=True, r=True)

    mc.xform(models_selected, piv=(0, 0, 0), ws=True)
    mc.scale(scale_ratio, scale_ratio, scale_ratio,
             models_selected, ws=True, r=True)


# set Automatic UVs

def auto_uvs():
    for model in models_selected:
        mc.polyAutoProjection(f"{model}.f[*]")


# soften Edges

def softEdges():
    for model in models_selected:
        mc.polySoftEdge(model, angle=180)

    mc.select(cl=True)


# freeze transformation

def freeze_tranfsorm():
    for model in models_selected:
        mc.makeIdentity(model, apply=True, t=1, r=1, s=1, n=0, pn=1)


# delete history

def delete_history():
    mc.delete(models_selected, ch=True)


# check symmetry

def check_symmetry():
    symmetry_script_path = os.path.join(
        os.path.dirname(__file__), 'mel', 'symmetry.mel').replace('\\', '/')

    mel.eval(f'source "{symmetry_script_path}"')


# delete shapeOrig and shapeDeformed

def delete_intermediate_objects():

    #model_sel = mc.ls(sl=1, type='transform')

    model_sel = models_selected

    for model in model_sel:
        # get all the transforms in hierarchy
        model_children = mc.ls(model, mc.listRelatives(
            model, ad=1, type='transform'))
        for model_child in model_children:
            # get the shapes of child
            model_child_shapes = mc.listRelatives(model_child, s=1)
            # do not delete if there is only one shape node
            if len(model_child_shapes) > 1:
                for model_child_shape in model_child_shapes:
                    # if nothing is connected to the shape node, delete it

                    if mc.getAttr(f"{model_child_shape}.intermediateObject"):
                        mc.delete(model_child_shape)

    mc.select(cl=True)


# delete the render and display layers

def delete_display_and_render_layers():

    display_layers = mc.ls(type='displayLayer')
    render_layers = mc.ls(type='renderLayer')

    for display_layer in display_layers:

        if len(display_layers) > 1 and display_layer != "defaultLayer":
            mc.editDisplayLayerMembers(display_layer)
            mc.delete(display_layer)

    for render_layer in render_layers:
        if len(render_layers) > 1 and render_layer != "defaultLayer":
            mc.delete(render_layer)



# delete unknown nodes

def delete_unknown_nodes():

    unknown_nodes = mc.ls(type = "unknown")

    for unknown_node in unknown_nodes:
        
        if mc.objExists(unknown_node):
            mc.delete(unknown_node)


# delete unused nodes in hypershade

def delete_unused_nodes():
    mel.eval("MLdeleteUnused")


# assignment material

def set_material(material_type, material_parms):

    faces = mc.ls(selection=True)
    shader = f"{material_type}_mat"
    sg = f"{material_type}_sg"
    
    if not mc.ls(sg): 
    
        shader = mc.shadingNode("blinn", asShader=True, name=shader )
        sg = mc.sets(empty=True, renderable=True, noSurfaceShader=True,  name=sg)
        mc.connectAttr( f"{shader}.outColor", f"{sg}.surfaceShader", f=True) 
      
    mc.sets(faces, e=True, forceElement=sg)
    
    for attr, value in material_parms.items():
        if isinstance(value, list):
            mc.setAttr(f"{shader}.{attr}", *value, type="double3")
        else:
            mc.setAttr(f"{shader}.{attr}", value)

'''
def set_material(material_type, material_color):

    faces = mc.ls(selection=True)
    shader = f"{material_type}_mat"
    sg = f"{material_type}_sg"
    
    if not mc.ls(sg): 
    
        shader = mc.shadingNode("blinn", asShader=True, name=shader )
        sg = mc.sets(empty=True, renderable=True, noSurfaceShader=True,  name=sg)
        mc.connectAttr( f"{shader}.outColor", f"{sg}.surfaceShader", f=True) 
      
    mc.sets(faces, e=True, forceElement=sg)
    
    mc.setAttr(f"{shader}.specularRollOff", 0.4)
    mc.setAttr(f"{shader}.reflectivity", 0.3)
    mc.setAttr(f"{shader}.eccentricity", 0.2)
    
    mc.setAttr(f"{shader}.color", material_color[0], material_color[1], material_color[2], type="double3")
'''

# set current units to cm

def check_current_unit():

    if mc.currentUnit(query=True, linear=True) != 'cm':
        mc.currentUnit(linear='cm')

    model_selection()


def query_inputs(height_field, *args):

    global model_height_target
    model_height_target = mc.floatField(height_field, q=True, v=1)


def grid_for_input_height():
    if mc.window('heightCheckDialog', ex=True):
        mc.deleteUI('heightCheckDialog', window=True)

    mc.window('heightCheckDialog', title='Height Check',
              sizeable=False, resizeToFitChildren=True)

    mc.rowColumnLayout(numberOfColumns=2, columnWidth=[
                       (1, 150), (2, 100), (3, 75)])

    height_label = mc.text(label='Height:', align='left')
    height_field = mc.floatField(value=175.0)

    mc.button(label='Apply', command=partial(query_inputs, height_field))

    mc.button(label='Cancel',
              command='mc.deleteUI("heightCheckDialog", window=True)')

    mc.showWindow()


def model_selection():

    global models_selected
    models_selected = mc.ls(selection=True, type='transform')

    if not models_selected:
        print("Please, select the model")
    # else:
        # grid_for_input_height()


# check_current_unit()
