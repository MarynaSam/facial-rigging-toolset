from importlib import reload
import maya.cmds as mc
from maya import OpenMaya as om


from facial_rig_toolset import body_head_blend
reload(body_head_blend)


MAIN_GROUP = "Face"
FACE_GROUP = ["Model", "Motion", "Dont"] 
DONT_GROUP = ["Fascia_grp", "Shapes_grp", "Infs_grp", "Deformers_grp", "Follicles_grp", "Eyelid_Setup_grp", "Clusters_grp"]
FASCIA_GROUP = ["Face_Shapes_geo", "Face_Infs_Local_geo", "Face_Infs_Broad_geo", "Face_Clusters_geo", "Face_Joints_geo", "Face_Deformers_geo", "Face_Follicles_geo", "Face_Wrap_geo"]
EYELID_SETUP_GROUP = ["Eyelid_Curves_grp","Eyelid_Locators_grp"]
HEAD_JNT = "_head_jnt"
BLEND_SHAPE = "_blendShape"
MODEL_NAME = body_head_blend.HEAD_GEOMETRY



def parent_mesh_under_model_group():

    meshes_to_parent = mc.ls(selection=True)

    if not meshes_to_parent:
        om.MGlobal.displayError("Please select the meshes you'd like to parent under 'Model'.")
        return

    mc.parent(meshes_to_parent, FACE_GROUP[0])


def parent_joints_under_motion_group():

    joints_to_parent = mc.ls(selection=True)

    if not joints_to_parent:
        om.MGlobal.displayError("Please select the joints you'd like to parent under 'Motion'.")
        return   

    mc.parent(joints_to_parent[0], FACE_GROUP[1])


def _name_and_parent_groups(list_of_names, grp_to_parent):
    
    for index in range(len(list_of_names)):
        mc.group(em=True, name=list_of_names[index])
        mc.parent(list_of_names[index], grp_to_parent)    

    mc.select(clear=True)


def _build_fascia_layers(list_of_names, grp_to_parent):

    if not mc.objExists(MODEL_NAME):
        om.MGlobal.displayError(f"Please rename your head model as '{MODEL_NAME}'.")
        return
    '''
    shape_orig = f"{MODEL_NAME}ShapeOrig"
    if mc.objExists(shape_orig):
        mc.delete(shape_orig)
    '''
    for fascia_layer_name in list_of_names:
        mc.duplicate(MODEL_NAME, n=fascia_layer_name)
        mc.parent(fascia_layer_name, grp_to_parent)

    fascia_first_layer = list_of_names[0:4]
    fascia_other_layers = list_of_names[4:] 
    
    print(fascia_first_layer)
    _connecting_fascia_layers(fascia_first_layer, list_of_names[4])

    for i in range(len(fascia_other_layers)):
        if i != (len(fascia_other_layers) - 1):
            fascia_top_layer = [fascia_other_layers[i]]
            fascia_lower_layer = fascia_other_layers[i+1]
            _connecting_fascia_layers(fascia_top_layer, fascia_lower_layer)
    '''
    blendshape_weights = []
    for i, _ in enumerate(fascia_first_layer):
        fire_blendshape_tuple = (i,1)
        blendshape_weights.append(fire_blendshape_tuple)

    blend_shape_name = f"{list_of_names[4]}{BLEND_SHAPE}"
    mc.blendShape(fascia_first_layer, list_of_names[4], topologyCheck=True, w=blendshape_weights, n=blend_shape_name)
    '''

def _connecting_fascia_layers(fascia_top_layer, fascia_lower_layer):

    blendshape_weights = []
    for i, _ in enumerate(fascia_top_layer):
        fire_blendshape_tuple = (i,1)
        blendshape_weights.append(fire_blendshape_tuple)

    blend_shape_name = f"{fascia_lower_layer}{BLEND_SHAPE}"
    mc.blendShape(fascia_top_layer, fascia_lower_layer, topologyCheck=True, w=blendshape_weights, n=blend_shape_name)


def build_structure():
    
    if mc.objExists(MAIN_GROUP):
        button = mc.confirmDialog(
            title="Face Group Exists",
            message="The Face Group already exists in the scene. However, it is not complete. Are you sure you want to re-create it?",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if button == "No":
            return
        else:
            mc.delete(MAIN_GROUP)

    mc.group(em=True, name=MAIN_GROUP)

    _name_and_parent_groups(FACE_GROUP, MAIN_GROUP)
    _name_and_parent_groups(DONT_GROUP, FACE_GROUP[2])
    _build_fascia_layers(FASCIA_GROUP, DONT_GROUP[0])
    _name_and_parent_groups(EYELID_SETUP_GROUP, DONT_GROUP[5])